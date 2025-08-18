import math

import pytest
from pyairtable.testing import fake_record

import bigger_picker.utils as utils


def test_fix_age_missing_mean_age():
    ds = fake_record(
        {
            "Mean Ages": [],
            "SD Ages": [],
            "Min Ages": 10.0,
            "Max Ages": 18.0,
        }
    )

    fixed_dataset = utils.fix_age(ds)
    assert fixed_dataset["fields"]["Mean Ages"] == 14.0
    assert fixed_dataset["fields"]["SD Ages"] == 2.0
    assert fixed_dataset["fields"]["Min Ages"] == 10.0
    assert fixed_dataset["fields"]["Max Ages"] == 18.0


def test_fix_age_missing_age_range():
    ds = fake_record(
        {
            "Mean Ages": ["15.0"],
            "SD Ages": ["1.5"],
            "Min Ages": 0,
            "Max Ages": 0,
        }
    )

    fixed_dataset = utils.fix_age(ds)
    assert fixed_dataset["fields"]["Mean Ages"] == 15.0
    assert fixed_dataset["fields"]["SD Ages"] == 1.5
    assert fixed_dataset["fields"]["Min Ages"] is None
    assert fixed_dataset["fields"]["Max Ages"] is None


def test_fix_year_missing_year():
    ds = fake_record(
        {
            "Year of Last Data Point": 0,
            "Earliest Publication": 2020,
        }
    )

    fixed_dataset = utils.fix_year(ds)
    assert fixed_dataset["fields"]["Year of Last Data Point"] == 2019
    assert fixed_dataset["fields"]["Earliest Publication"] == 2020


def test_fix_dataset():
    ds = fake_record(
        {
            "Mean Ages": [],
            "SD Ages": [],
            "Min Ages": 10.0,
            "Max Ages": 18.0,
            "Year of Last Data Point": 0,
            "Earliest Publication": 2020,
        }
    )
    fixed_dataset = utils.fix_dataset(ds)
    assert fixed_dataset["fields"]["Mean Ages"] == 14.0
    assert fixed_dataset["fields"]["SD Ages"] == 2.0
    assert fixed_dataset["fields"]["Min Ages"] == 10.0
    assert fixed_dataset["fields"]["Max Ages"] == 18.0
    assert fixed_dataset["fields"]["Year of Last Data Point"] == 2019
    assert fixed_dataset["fields"]["Earliest Publication"] == 2020


def test_compute_dataset_value_no_included():
    ds = fake_record({"Total Sample Size": 400, "Year of Last Data Point": 2020})
    included = []
    potential = [ds]

    # Default weights: alpha=1 / math.log(1000), epsilon=1
    expected_size = (1 / math.log(1000)) * math.log(400 + 1)
    # years = [2020], so y_min == y_max => R_i = 1
    expected_recency = 1.0
    expected = expected_size + expected_recency

    value = utils.compute_dataset_value(ds, included, potential)
    assert pytest.approx(value, rel=1e-6) == expected


def test_compute_dataset_value_recency_scaling():
    ds_new = fake_record({"Total Sample Size": 400, "Year of Last Data Point": 2020})
    ds_old = fake_record({"Total Sample Size": 400, "Year of Last Data Point": 2000})
    included = []
    potential = [ds_new, ds_old]

    df_new_val = utils.compute_dataset_value(ds_new, included, potential)
    df_old_val = utils.compute_dataset_value(ds_old, included, potential)

    assert df_new_val > df_old_val, "Newer dataset should have higher value"


def test_compute_dataset_value_outcome_term():
    included = [fake_record({"Total Sample Size": 50, "Articles: Outcomes": ["X"]})]
    candidate = fake_record(
        {
            "Total Sample Size": 0,
            "Year of Last Data Point": 2021,
            "Articles: Outcomes": ["X", "Y"],
            "Mean Ages": None,
            "SD Ages": None,
        }
    )
    weights = {"alpha": 0.0, "beta": 1.0, "gamma": 0.0, "delta": 0.0, "epsilon": 0.0}
    potential = [candidate]

    # coverage: X→50, Y→0 → O_i = (1/(1+50) + 1/(1+0)) / 2
    expected_O = (1 / (1 + 50) + 1) / 2
    val = utils.compute_dataset_value(candidate, included, potential, weights=weights)
    assert pytest.approx(val, rel=1e-6) == expected_O


def test_compute_dataset_value_age_term():
    # One included dataset with mean=10, sd=0.1, N=100
    included = [
        fake_record(
            {
                "Total Sample Size": 100,
                "Mean Ages": 10.0,
                "SD Ages": 0.1,
                "Articles: Outcomes": [],
            }
        )
    ]
    # Candidate with same mean=10, sd=0.1
    candidate = fake_record(
        {
            "Total Sample Size": 0,
            "Year of Last Data Point": 2021,
            "Articles: Outcomes": [],
            "Mean Ages": 10.0,
            "SD Ages": 0.1,
        }
    )
    # Weights to isolate age term
    weights = {"alpha": 0.0, "beta": 0.0, "gamma": 1.0, "delta": 0.0, "epsilon": 0.0}
    potential = [candidate]

    # Since distributions align perfectly, CovWeighted = 100 → A_i = 1/(1+100)
    expected_A = 1 / (1 + 100)
    val = utils.compute_dataset_value(candidate, included, potential, weights=weights)
    assert pytest.approx(val, rel=1e-6) == expected_A


def test_identify_duplicate_datasets_exact_match():
    # Test with exact duplicates
    dataset1 = fake_record(
        {
            "Dataset Name": "Study A",
            "Dataset Contact Name": "John Doe",
            "Dataset Contact Email": "john@example.com",
        }
    )
    dataset2 = fake_record(
        {
            "Dataset Name": "Study A",
            "Dataset Contact Name": "John Doe",
            "Dataset Contact Email": "john@example.com",
        }
    )

    datasets = [dataset1, dataset2]
    duplicates = utils.identify_duplicate_datasets(datasets, threshold=0.9)

    assert dataset1["id"] in duplicates
    assert dataset2["id"] in duplicates
    assert dataset2["id"] in duplicates[dataset1["id"]]
    assert dataset1["id"] in duplicates[dataset2["id"]]


def test_identify_duplicate_datasets_similar_names():
    dataset1 = fake_record(
        {
            "Dataset Name": "Study ABC",
            "Dataset Contact Name": "Jane Smith",
            "Dataset Contact Email": "jane@example.com",
        }
    )
    dataset2 = fake_record(
        {
            "Dataset Name": "Study ABD",
            "Dataset Contact Name": "Jane Smith",
            "Dataset Contact Email": "jane@example.com",
        }
    )

    datasets = [dataset1, dataset2]
    duplicates = utils.identify_duplicate_datasets(datasets, threshold=0.7)

    # Should identify as duplicates due to similar names and same contact
    assert dataset1["id"] in duplicates
    assert dataset2["id"] in duplicates


def test_identify_duplicate_datasets_email_match():
    # Test with same email but different names
    dataset1 = fake_record(
        {
            "Dataset Name": "Different Study 1",
            "Dataset Contact Name": "Alice Johnson",
            "Dataset Contact Email": "researcher@university.edu",
        }
    )
    dataset2 = fake_record(
        {
            "Dataset Name": "Different Study 2",
            "Dataset Contact Name": "Bob Wilson",
            "Dataset Contact Email": "researcher@university.edu",
        }
    )

    datasets = [dataset1, dataset2]
    duplicates = utils.identify_duplicate_datasets(datasets, threshold=0.3)

    # Should identify as duplicates due to same email
    assert dataset1["id"] in duplicates
    assert dataset2["id"] in duplicates


def test_identify_duplicate_datasets_no_duplicates():
    # Test with completely different datasets
    dataset1 = fake_record(
        {
            "Dataset Name": "Alpha, 2018",
            "Dataset Contact Name": "John Alpha",
            "Dataset Contact Email": "alpha@university1.edu",
        }
    )
    dataset2 = fake_record(
        {
            "Dataset Name": "Beta, 2019",
            "Dataset Contact Name": "Joanne beta",
            "Dataset Contact Email": "beta@university2.edu",
        }
    )

    datasets = [dataset1, dataset2]
    duplicates = utils.identify_duplicate_datasets(datasets, threshold=0.51)

    # Should not identify any duplicates
    assert len(duplicates) == 0


def test_identify_duplicate_datasets_missing_fields():
    # Test with missing contact information
    dataset1 = fake_record(
        {
            "Dataset Name": "Study with Missing Info",
            "Dataset Contact Name": None,
            "Dataset Contact Email": None,
        }
    )
    dataset2 = fake_record(
        {
            "Dataset Name": "Study with Missing Info",
            "Dataset Contact Name": "",
            "Dataset Contact Email": "",
        }
    )

    datasets = [dataset1, dataset2]
    duplicates = utils.identify_duplicate_datasets(datasets, threshold=0.5)

    # Should still identify duplicates based on dataset name similarity
    assert dataset1["id"] in duplicates
    assert dataset2["id"] in duplicates


def test_identify_duplicate_datasets_custom_threshold():
    # Test with custom threshold
    dataset1 = fake_record(
        {
            "Dataset Name": "Study ABC",
            "Dataset Contact Name": "Researcher One",
            "Dataset Contact Email": "one@example.com",
        }
    )
    dataset2 = fake_record(
        {
            "Dataset Name": "Study XYZ",
            "Dataset Contact Name": "Researcher Two",
            "Dataset Contact Email": "two@example.com",
        }
    )

    datasets = [dataset1, dataset2]

    # With high threshold, should not match
    duplicates_high = utils.identify_duplicate_datasets(datasets, threshold=0.9)
    assert len(duplicates_high) == 0

    # With very low threshold, should match (even dissimilar records)
    duplicates_low = utils.identify_duplicate_datasets(datasets, threshold=0.01)
    assert len(duplicates_low) > 0


def test_identify_duplicate_datasets_large_dataset():
    # Test with larger dataset to trigger different indexing strategy
    datasets = []
    for i in range(50):
        dataset = fake_record(
            {
                "Dataset Name": f"Study {i}",
                "Dataset Contact Name": f"Researcher {i}",
                "Dataset Contact Email": f"researcher{i}@example.com",
            }
        )
        datasets.append(dataset)

    # Add a duplicate
    duplicate = fake_record(
        {
            "Dataset Name": "Study 0",
            "Dataset Contact Name": "Researcher 0",
            "Dataset Contact Email": "researcher0@example.com",
        }
    )
    datasets.append(duplicate)

    duplicates = utils.identify_duplicate_datasets(datasets, threshold=0.5)

    # Should find the duplicate
    assert datasets[0]["id"] in duplicates
    assert duplicate["id"] in duplicates
