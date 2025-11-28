import logging
import math
import unicodedata
from collections import defaultdict
from datetime import datetime
from logging.handlers import RotatingFileHandler

import pandas as pd
import recordlinkage
from pyairtable.api.types import RecordDict
from rich.table import Table


def setup_logger(
    name: str = "bigger_picker", log_file: str = "bigger_picker.log"
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def sanitize_text(text: str | None) -> str:
    if not text:
        return ""
    replacements = {
        "\u2018": "'",  # Left single quote
        "\u2019": "'",  # Right single quote
        "\u201c": '"',  # Left double quote
        "\u201d": '"',  # Right double quote
        "\u2013": "-",  # En-dash
        "\u2014": "-",  # Em-dash
        "…": "...",  # Ellipsis
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.replace("\n", " ").replace("\r", "")

    return " ".join(text.split())


def fix_age(dataset: RecordDict) -> RecordDict:
    fields = dataset["fields"]

    fields["Mean Ages"] = float(fields["Mean Ages"][0]) if fields["Mean Ages"] else None
    fields["SD Ages"] = float(fields["SD Ages"][0]) if fields["SD Ages"] else None

    fields["Min Ages"] = (
        None
        if fields["Min Ages"] == 0 or fields["Min Ages"] < 0
        else fields["Min Ages"]
    )
    fields["Max Ages"] = (
        None
        if fields["Max Ages"] == 0 or fields["Max Ages"] > 18
        else fields["Max Ages"]
    )

    if fields["Min Ages"] and fields["Max Ages"]:
        # If we have both the min and max, we can estimate missing means and SDs
        if not fields["Mean Ages"]:
            # Just use the mid point
            fields["Mean Ages"] = (fields["Min Ages"] + fields["Max Ages"]) / 2

        if not fields["SD Ages"]:
            # Estimate the SD as a quarter of the range
            fields["SD Ages"] = (fields["Max Ages"] - fields["Min Ages"]) / 4

    # If the mean is outside the allowed range, set to None
    if fields["Mean Ages"] is not None:
        if fields["Mean Ages"] > 18 or fields["Mean Ages"] < 0:
            fields["Mean Ages"] = None
            fields["SD Ages"] = None

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


def compute_size_value(dataset: RecordDict) -> float:
    N_i = dataset["fields"].get("Total Sample Size", 0)
    return math.log(N_i + 1)


def compute_outcome_value(dataset: RecordDict) -> int:
    return len(dataset["fields"].get("Searches", []))


def compute_year_range(
    datasets_included: list[RecordDict],
    datasets_potential: list[RecordDict],
) -> tuple[int | None, int | None]:
    years = {
        year
        for dset in datasets_potential + datasets_included
        if (year := dset["fields"].get("Year of Last Data Point")) is not None
        and year > 1950
    }

    if years:
        return min(years), max(years)  # type: ignore
    else:
        return None, None


def compute_year_value(
    dataset: RecordDict,
    y_min: int | None,
    y_max: int | None,
) -> float:
    if y_min is None or y_max is None:
        return 0.5

    year_last = dataset["fields"].get("Year of Last Data Point")
    if year_last is None:
        return 0.5

    if y_max > y_min:
        R_i = (dataset["fields"]["Year of Last Data Point"] - y_min) / (y_max - y_min)
    else:
        R_i = 0.5

    return R_i


def compute_age_cache(
    datasets_included: list[RecordDict],
) -> dict[str, tuple[float, float, int]]:
    cache = {}
    for dset in datasets_included:
        mean_j = dset["fields"].get("Mean Ages")
        sd_j = dset["fields"].get("SD Ages")
        N_j = dset["fields"].get("Total Sample Size", 0)
        if mean_j is not None and sd_j is not None and sd_j > 0:
            cache[dset["id"]] = (mean_j, sd_j, N_j)

    return cache


def compute_age_value(dataset: RecordDict, age_cache: dict | None) -> float:
    if age_cache is None:
        return 0.0

    mean_i = dataset["fields"].get("Mean Ages")
    sd_i = dataset["fields"].get("SD Ages")
    if mean_i is None or sd_i is None or sd_i <= 0:
        return 0.0

    a_min = int(math.floor(mean_i - 3 * sd_i))
    a_max = int(math.ceil(mean_i + 3 * sd_i))
    ages = list(range(a_min, a_max + 1))

    Cov = {a: 0.0 for a in ages}
    total_N = 0
    n_dsets = 0

    for mean_j, sd_j, N_j in age_cache.values():
        total_N += N_j
        n_dsets += 1
        wj_unnorm = [math.exp(-((a - mean_j) ** 2) / (2 * sd_j**2)) for a in ages]
        total_wj = sum(wj_unnorm)
        if total_wj == 0:
            continue
        wj = [w / total_wj for w in wj_unnorm]

        for a, w in zip(ages, wj, strict=False):
            Cov[a] += N_j * w

    wi_unnorm = [math.exp(-((a - mean_i) ** 2) / (2 * sd_i**2)) for a in ages]
    total_wi = sum(wi_unnorm)
    if total_wi == 0:
        return 0.0

    wi = [w / total_wi for w in wi_unnorm]
    CovWeighted = sum(Cov[a] * w for a, w in zip(ages, wi, strict=False))
    if n_dsets == 0:
        return 0.0
    avg_N = total_N / n_dsets
    coverage_scaled = CovWeighted / avg_N
    A_i = 1.0 / (1.0 + coverage_scaled)

    return A_i


def compute_dataset_value(
    dataset: RecordDict,
    year_min: int | None,
    year_max: int | None,
    age_cache: dict | None,
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

    N_i = compute_size_value(dataset)
    R_i = compute_year_value(dataset, year_min, year_max)
    O_i = compute_outcome_value(dataset)
    A_i = compute_age_value(dataset, age_cache)
    S_i = O_i * A_i

    size_term = N_i * alpha
    recency_term = R_i * epsilon
    outcome_term = O_i * beta
    age_term = A_i * gamma
    synergy_term = S_i * delta

    # Sum everything
    return size_term + outcome_term + age_term + synergy_term + recency_term


def identify_duplicate_datasets(
    datasets: list[RecordDict], threshold: float = 0.5
) -> dict[str, list[str]]:
    logging.getLogger("recordlinkage").setLevel(logging.ERROR)
    df = pd.json_normalize(datasets)  # type: ignore

    df_clean = df.copy()
    df_clean["fields.Dataset Name"] = (
        df_clean["fields.Dataset Name"].fillna("").str.strip()
    )
    df_clean["fields.Dataset Contact Name"] = (
        df_clean["fields.Dataset Contact Name"].str.strip().mask(lambda x: x == "")
    )
    df_clean["fields.Dataset Contact Email"] = (
        df_clean["fields.Dataset Contact Email"].str.strip().mask(lambda x: x == "")
    )
    # Choose indexing strategy based on size
    indexer = recordlinkage.Index()

    n_rows = len(df_clean)

    if n_rows < 1000:
        # Small dataset: compare everything
        indexer.full()
        candidate_pairs = indexer.index(df_clean)

    else:
        # Medium dataset: multiple loose blocking
        window_size = 9 if n_rows < 3000 else 5
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


def create_stats_table(stats: dict) -> Table:
    def make_subtable(subgroups: dict, substats: dict) -> Table:
        platform_table = Table(show_header=False, show_edge=False)
        for key, value in subgroups.items():
            platform_table.add_row(value, str(substats[key]))
        return platform_table

    # Main table
    table = Table(
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
        title="Bigger Picker Status",
    )
    table.add_column("Metric", style="cyan", vertical="middle")
    table.add_column("Value", style="green", vertical="middle", justify="center")
    uptime = str(datetime.now() - stats["start_time"]).split(".")[0]
    table.add_row("Status", stats["status"])
    table.add_row("Uptime", uptime)
    table.add_row("Platforms", stats["platforms"])

    # Subtables
    platforms_dict = {"asana": "Asana", "rayyan": "Rayyan", "openai": "OpenAI"}
    last_check_table = make_subtable(platforms_dict, stats["last_check"])
    table.add_row("Last Check", last_check_table)
    last_sync_table = make_subtable(platforms_dict, stats["last_sync"])
    table.add_row("Last Sync", last_sync_table)
    total_syncs_table = make_subtable(platforms_dict, stats["total_syncs"])
    table.add_row("Total Syncs", total_syncs_table)
    total_polls_table = make_subtable(platforms_dict, stats["total_polls"])
    table.add_row("Total Polls", total_polls_table)
    pending_batches_table = make_subtable(
        {
            "abstracts": "Abstracts",
            "fulltexts": "Fulltexts",
            "extractions": "Extractions",
        },
        stats["pending_batches"],
    )
    table.add_row("Pending Batches", pending_batches_table)

    return table
