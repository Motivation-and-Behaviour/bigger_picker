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
    # One included dataset with outcome 'X' and sample size 50
    included = [fake_record({"Total Sample Size": 50, "Articles: Outcomes": ["X"]})]
    # Candidate with outcomes 'X' and 'Y'
    candidate = fake_record(
        {
            "Total Sample Size": 0,
            "Year of Last Data Point": 2021,
            "Articles: Outcomes": ["X", "Y"],
            "Mean Ages": None,
            "SD Ages": None,
        }
    )
    # Weights to isolate outcome term
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
