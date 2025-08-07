import math

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
) -> list[tuple[str, str]]:
    df = pd.json_normalize(datasets)  # type: ignore

    # Clean the data
    df_clean = df.copy()
    df_clean["fields.Dataset Name"] = (
        df_clean["fields.Dataset Name"].fillna("").str.strip()
    )
    df_clean["fields.Dataset Contact Name"] = (
        df_clean["fields.Dataset Contact Name"].fillna("").str.strip()
    )
    df_clean["fields.Dataset Contact Email"] = (
        df_clean["fields.Dataset Contact Email"].fillna("").str.strip()
    )
    df_clean["fields.Total Sample Size"] = pd.to_numeric(
        df_clean["fields.Total Sample Size"], errors="coerce"
    )

    # Choose indexing strategy based on size
    indexer = recordlinkage.Index()

    if len(df_clean) < 1000:
        # Small dataset: compare everything
        indexer.full()
        candidate_pairs = indexer.index(df_clean)

    elif len(df_clean) < 3000:
        # Medium dataset: multiple loose blocking
        indexer.sortedneighbourhood("fields.Dataset Name", window=10)

        # Add email blocking
        indexer_email = recordlinkage.Index()
        indexer_email.block("fields.Dataset Contact Email")

        # Combine pairs
        pairs1 = indexer.index(df_clean)
        pairs2 = indexer_email.index(df_clean)
        candidate_pairs = pairs1.union(pairs2)

    else:
        # Larger dataset: tighter blocking
        indexer.sortedneighbourhood("fields.Dataset Name", window=5)

        indexer_contact = recordlinkage.Index()
        indexer_contact.block("fields.Dataset Contact Name")

        pairs1 = indexer.index(df_clean)
        pairs2 = indexer_contact.index(df_clean)
        candidate_pairs = pairs1.union(pairs2)

    if len(candidate_pairs) == 0:
        return []

    # Set up comparisons
    compare = recordlinkage.Compare()

    compare.string(
        "fields.Dataset Name",
        "fields.Dataset Name",
        method="jarowinkler",
        threshold=0.6,
        label="dataset_name_sim",
    )

    compare.string(
        "fields.Dataset Contact Name",
        "fields.Dataset Contact Name",
        method="jarowinkler",
        threshold=0.7,
        label="contact_name_sim",
    )

    compare.exact(
        "fields.Dataset Contact Email",
        "fields.Dataset Contact Email",
        label="email_exact",
    )

    # Numeric comparison for sample size
    compare.numeric(
        "fields.Total Sample Size",
        "fields.Total Sample Size",
        method="gauss",
        offset=0,
        scale=100,
        label="sample_size_sim",
    )

    # Compute comparison vectors
    comparison_vectors = compare.compute(candidate_pairs, df_clean)

    # Calculate composite scores
    scores = (
        comparison_vectors["dataset_name_sim"] * 0.4
        + comparison_vectors["contact_name_sim"] * 0.1
        + comparison_vectors["email_exact"] * 0.3
        + comparison_vectors["sample_size_sim"] * 0.1
    )

    # Build results DataFrame
    results = []
    for (idx1, idx2), row in comparison_vectors.iterrows():
        score = scores.loc[(idx1, idx2)]

        # Only include pairs above a minimum threshold to reduce noise
        if score >= 0.2:  # Very low threshold to catch most potential matches
            result = {
                "record_1_id": df_clean.loc[idx1, "id"],
                "record_2_id": df_clean.loc[idx2, "id"],
                "dataset_name_1": df_clean.loc[idx1, "fields.Dataset Name"],
                "dataset_name_2": df_clean.loc[idx2, "fields.Dataset Name"],
                "contact_name_1": df_clean.loc[idx1, "fields.Dataset Contact Name"],
                "contact_name_2": df_clean.loc[idx2, "fields.Dataset Contact Name"],
                "email_1": df_clean.loc[idx1, "fields.Dataset Contact Email"],
                "email_2": df_clean.loc[idx2, "fields.Dataset Contact Email"],
                "sample_size_1": df_clean.loc[idx1, "fields.Total Sample Size"],
                "sample_size_2": df_clean.loc[idx2, "fields.Total Sample Size"],
                "dataset_name_similarity": row["dataset_name_sim"],
                "contact_name_similarity": row["contact_name_sim"],
                "email_match": row["email_exact"],
                "sample_size_similarity": row["sample_size_sim"],
                "composite_score": score,
                "likely_duplicate": score >= threshold,
            }
            results.append(result)

    if not results:
        print("No potential duplicates found above minimum threshold!")
        return pd.DataFrame()

    # Convert to DataFrame and sort
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("composite_score", ascending=False)

    # Print summary
    total_matches = len(results_df[results_df["likely_duplicate"]])
    high_conf = len(results_df[results_df["composite_score"] > 0.8])
    medium_conf = len(
        results_df[
            (results_df["composite_score"] > threshold)
            & (results_df["composite_score"] <= 0.8)
        ]
    )

    return results_df
