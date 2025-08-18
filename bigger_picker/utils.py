import math
from collections import defaultdict

import numpy as np
import pandas as pd
import recordlinkage
from pyairtable.api.types import RecordDict


def fix_age(dataset: RecordDict) -> RecordDict:
    fields = dataset["fields"]

    fields["Mean Ages"] = float(fields["Mean Ages"][0]) if fields["Mean Ages"] else None
    fields["SD Ages"] = float(fields["SD Ages"][0]) if fields["SD Ages"] else None

    fields["Min Ages"] = None if fields["Min Ages"] == 0 else fields["Min Ages"]
    fields["Max Ages"] = None if fields["Max Ages"] == 0 else fields["Max Ages"]

    if fields["Min Ages"] and fields["Max Ages"]:
        # If we have both the min and max, we can estimate missing means and SDs
        if not fields["Mean Ages"]:
            # Just use the mid point
            fields["Mean Ages"] = (fields["Min Ages"] + fields["Max Ages"]) / 2

        if not fields["SD Ages"]:
            # Estimate the SD as a quarter of the range
            fields["SD Ages"] = (fields["Max Ages"] - fields["Min Ages"]) / 4

    dataset["fields"] = fields
    return dataset


def fix_year(dataset: RecordDict) -> RecordDict:
    if dataset["fields"]["Year of Last Data Point"] == 0:
        dataset["fields"]["Year of Last Data Point"] = (
            dataset["fields"]["Earliest Publication"] - 1
        )
    return dataset


def fix_dataset(dataset: RecordDict) -> RecordDict:
    dataset = fix_age(dataset)
    dataset = fix_year(dataset)
    return dataset


def compute_dataset_value(
    dataset: RecordDict,
    datasets_included: list[RecordDict],
    datasets_potential: list[RecordDict],
    weights: dict[str, float] | None = None,
) -> float:
    """
    Compute the prioritisation value for `dataset` given:
      - datasets_included: list of already-included datasets (may be empty)
      - datasets_potential: list of all candidate datasets

    Returns
    -------
    float
      Value_i = alpha·ln(N_i+1) + beta·O_i + gamma·A_i + delta·(O_i·A_i) + epsilon·R_i
    """
    # Default weights
    alpha = weights["alpha"] if weights and "alpha" in weights else 1 / math.log(1000)
    beta = weights["beta"] if weights and "beta" in weights else 1
    gamma = weights["gamma"] if weights and "gamma" in weights else 1
    delta = weights["delta"] if weights and "delta" in weights else 2
    epsilon = weights["epsilon"] if weights and "epsilon" in weights else 1

    # Sample size term
    N_i = dataset["fields"].get("Total Sample Size", 0)
    size_term = alpha * math.log(N_i + 1)

    # Recency term: R_i
    years = [
        dset["fields"].get("Year of Last Data Point")
        for dset in datasets_potential + datasets_included
        if dset["fields"].get("Year of Last Data Point") is not None
    ]
    if years:
        y_min, y_max = min(years), max(years)  # type: ignore
        if y_max > y_min:
            R_i = (dataset["fields"]["Year of Last Data Point"] - y_min) / (
                y_max - y_min
            )
        else:
            R_i = 1.0
    else:
        R_i = 1.0
    recency_term = epsilon * R_i

    # If no datasets are yet included, skip O_i, A_i, S_i
    if not datasets_included:
        return size_term + recency_term

    # Outcome‐need term
    # average over all outcomes in this dataset
    outcomes_i = dataset["fields"].get("Articles: Outcomes", [])
    # build coverage map: outcome -> total N in included datasets
    coverage = {}
    for dset in datasets_included:
        Nj = dset["fields"].get("Total Sample Size", 0)
        for outcome in dset["fields"].get("Articles: Outcomes", []):
            coverage[outcome] = coverage.get(outcome, 0) + Nj

    outcome_list = [1.0 / (1.0 + coverage.get(outcome, 0)) for outcome in outcomes_i]
    O_i = sum(outcome_list) / len(outcome_list) if outcome_list else 0.0
    outcome_term = beta * O_i

    # Age‐need term: A_i
    mean_i = dataset["fields"].get("Mean Ages")
    sd_i = dataset["fields"].get("SD Ages")
    if mean_i is None or sd_i is None or sd_i <= 0:
        A_i = 0.0
    else:
        # discretise ages from mean_i±3sd_i
        a_min = int(math.floor(mean_i - 3 * sd_i))
        a_max = int(math.ceil(mean_i + 3 * sd_i))
        ages = list(range(a_min, a_max + 1))

        # build Cov(a) = sum_j [ N_j * weight_j(a) ]
        Cov = {a: 0.0 for a in ages}
        for d in datasets_included:
            mean_j = d["fields"].get("Mean Ages")
            sd_j = d["fields"].get("SD Ages")
            N_j = d["fields"].get("Total Sample Size", 0)
            if mean_j is None or sd_j is None or sd_j <= 0:
                continue

            # weights for dataset j over the same age grid
            wj_unnorm = [math.exp(-((a - mean_j) ** 2) / (2 * sd_j**2)) for a in ages]
            total_wj = sum(wj_unnorm)
            if total_wj == 0:
                continue
            wj = [w / total_wj for w in wj_unnorm]

            for a, w in zip(ages, wj, strict=False):
                Cov[a] += N_j * w

        # now weight Cov(a) by this dataset’s own age‐distribution
        wi_unnorm = [math.exp(-((a - mean_i) ** 2) / (2 * sd_i**2)) for a in ages]
        total_wi = sum(wi_unnorm)
        if total_wi == 0:
            A_i = 0.0
        else:
            wi = [w / total_wi for w in wi_unnorm]
            CovWeighted = sum(Cov[a] * w for a, w in zip(ages, wi, strict=False))
            A_i = 1.0 / (1.0 + CovWeighted)

    age_term = gamma * A_i

    # Synergy term: S_i = O_i * A_i
    synergy_term = delta * (O_i * A_i)

    # Sum everything
    return size_term + outcome_term + age_term + synergy_term + recency_term


def identify_duplicate_datasets(
    datasets: list[RecordDict], threshold: float = 0.5
) -> dict[str, list[str]]:
    df = pd.json_normalize(datasets)  # type: ignore

    df_clean = df.copy()
    df_clean["fields.Dataset Name"] = (
        df_clean["fields.Dataset Name"].fillna("").str.strip()
    )
    df_clean["fields.Dataset Contact Name"] = (
        df_clean["fields.Dataset Contact Name"].str.strip().replace("", np.nan)
    )
    df_clean["fields.Dataset Contact Email"] = (
        df_clean["fields.Dataset Contact Email"].str.strip().replace("", np.nan)
    )
    # Choose indexing strategy based on size
    indexer = recordlinkage.Index()

    n_rows = len(df_clean)

    window_size = 10 if n_rows < 3000 else 5

    if n_rows < 1000:
        # Small dataset: compare everything
        indexer.full()
        candidate_pairs = indexer.index(df_clean)

    else:
        # Medium dataset: multiple loose blocking
        indexer.sortedneighbourhood("fields.Dataset Name", window=window_size)

        # Add email blocking
        indexer_email = recordlinkage.Index()
        indexer_email.block("fields.Dataset Contact Email")

        # Combine pairs
        pairs1 = indexer.index(df_clean)
        pairs2 = indexer_email.index(df_clean)
        if pairs1 is not None and pairs2 is not None:
            candidate_pairs = pairs1.union(pairs2)
        elif pairs1 is not None:
            candidate_pairs = pairs1
        elif pairs2 is not None:
            candidate_pairs = pairs2
        else:
            candidate_pairs = pd.MultiIndex.from_tuples(
                [], names=["rec_id_1", "rec_id_2"]
            )

    compare = recordlinkage.Compare()

    # String comparisons - adjust thresholds based on dataset size
    name_threshold = 0.6 if n_rows < 1000 else 0.7
    contact_threshold = 0.7 if n_rows < 1000 else 0.75

    compare.string(
        "fields.Dataset Name",
        "fields.Dataset Name",
        method="jarowinkler",
        threshold=name_threshold,
        label="dataset_name_sim",
    )

    compare.string(
        "fields.Dataset Contact Name",
        "fields.Dataset Contact Name",
        method="jarowinkler",
        threshold=contact_threshold,
        label="contact_name_sim",
    )

    compare.exact(
        "fields.Dataset Contact Email",
        "fields.Dataset Contact Email",
        label="email_exact",
    )

    comparison_vectors = compare.compute(candidate_pairs, df_clean)

    scores = (
        comparison_vectors["dataset_name_sim"] * 0.5  # Increased weight
        + comparison_vectors["contact_name_sim"] * 0.3  # Same weight
        + comparison_vectors["email_exact"] * 0.2  # Same weight
    )

    results = defaultdict(list)
    for idx1, idx2 in comparison_vectors.index:
        score = scores.loc[(idx1, idx2)]

        if score >= threshold:
            results[df_clean.loc[idx1, "id"]].append(df_clean.loc[idx2, "id"])
            results[df_clean.loc[idx2, "id"]].append(df_clean.loc[idx1, "id"])

    return results
