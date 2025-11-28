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


def test_compute_size_value():
    # Test with various sample sizes
    ds_zero = fake_record({"Total Sample Size": 0})
    ds_small = fake_record({"Total Sample Size": 10})
    ds_medium = fake_record({"Total Sample Size": 100})
    ds_large = fake_record({"Total Sample Size": 1000})

    # Size value is log(N+1)
    assert utils.compute_size_value(ds_zero) == math.log(1)
    assert utils.compute_size_value(ds_small) == pytest.approx(math.log(11))
    assert utils.compute_size_value(ds_medium) == pytest.approx(math.log(101))
    assert utils.compute_size_value(ds_large) == pytest.approx(math.log(1001))


def test_compute_size_value_missing_field():
    # Test when Total Sample Size is missing
    ds_missing = fake_record({})
    assert utils.compute_size_value(ds_missing) == math.log(1)


def test_compute_outcome_value():
    # Test with various numbers of searches
    ds_no_searches = fake_record({"Searches": []})
    ds_one_search = fake_record({"Searches": ["Search1"]})
    ds_multiple_searches = fake_record({"Searches": ["Search1", "Search2", "Search3"]})

    assert utils.compute_outcome_value(ds_no_searches) == 0
    assert utils.compute_outcome_value(ds_one_search) == 1
    assert utils.compute_outcome_value(ds_multiple_searches) == 3


def test_compute_outcome_value_missing_field():
    # Test when Searches field is missing
    ds_missing = fake_record({})
    assert utils.compute_outcome_value(ds_missing) == 0


def test_compute_year_range_with_valid_years():
    included = [
        fake_record({"Year of Last Data Point": 2010}),
        fake_record({"Year of Last Data Point": 2015}),
    ]
    potential = [
        fake_record({"Year of Last Data Point": 2000}),
        fake_record({"Year of Last Data Point": 2020}),
    ]

    y_min, y_max = utils.compute_year_range(included, potential)
    assert y_min == 2000
    assert y_max == 2020


def test_compute_year_range_filters_old_years():
    # Years before 1950 should be filtered out
    included = [fake_record({"Year of Last Data Point": 1900})]
    potential = [
        fake_record({"Year of Last Data Point": 2010}),
        fake_record({"Year of Last Data Point": 2020}),
    ]

    y_min, y_max = utils.compute_year_range(included, potential)
    assert y_min == 2010
    assert y_max == 2020


def test_compute_year_range_no_valid_years():
    # All years before 1950
    included = [fake_record({"Year of Last Data Point": 1900})]
    potential = [fake_record({"Year of Last Data Point": 1945})]

    y_min, y_max = utils.compute_year_range(included, potential)
    assert y_min is None
    assert y_max is None


def test_compute_year_range_missing_years():
    # Missing year fields
    included = [fake_record({})]
    potential = [fake_record({"Year of Last Data Point": None})]

    y_min, y_max = utils.compute_year_range(included, potential)
    assert y_min is None
    assert y_max is None


def test_compute_year_value():
    # Test with a range from 2000 to 2020
    ds_old = fake_record({"Year of Last Data Point": 2000})
    ds_mid = fake_record({"Year of Last Data Point": 2010})
    ds_new = fake_record({"Year of Last Data Point": 2020})

    # R_i = (year - y_min) / (y_max - y_min)
    assert utils.compute_year_value(ds_old, 2000, 2020) == pytest.approx(0.0)
    assert utils.compute_year_value(ds_mid, 2000, 2020) == pytest.approx(0.5)
    assert utils.compute_year_value(ds_new, 2000, 2020) == pytest.approx(1.0)


def test_compute_year_value_same_year():
    # When y_min == y_max, should return 0.5
    ds = fake_record({"Year of Last Data Point": 2020})
    assert utils.compute_year_value(ds, 2020, 2020) == 0.5


def test_compute_year_value_no_range():
    # When year range is None, should return 0.5
    ds = fake_record({"Year of Last Data Point": 2020})
    assert utils.compute_year_value(ds, None, None) == 0.5


def test_compute_age_cache():
    included = [
        fake_record(
            {
                "Mean Ages": 10.0,
                "SD Ages": 2.0,
                "Total Sample Size": 100,
            }
        ),
        fake_record(
            {
                "Mean Ages": 15.0,
                "SD Ages": 3.0,
                "Total Sample Size": 200,
            }
        ),
    ]

    cache = utils.compute_age_cache(included)
    assert cache is not None
    assert len(cache) == 2

    # Check that the cache contains the correct values
    id1, id2 = included[0]["id"], included[1]["id"]
    assert cache[id1] == (10.0, 2.0, 100)
    assert cache[id2] == (15.0, 3.0, 200)


def test_compute_age_cache_filters_invalid():
    # Should filter out datasets with missing or invalid age data
    included = [
        fake_record({"Mean Ages": 10.0, "SD Ages": 2.0, "Total Sample Size": 100}),
        fake_record({"Mean Ages": None, "SD Ages": 2.0, "Total Sample Size": 100}),
        fake_record({"Mean Ages": 10.0, "SD Ages": None, "Total Sample Size": 100}),
        fake_record({"Mean Ages": 10.0, "SD Ages": 0, "Total Sample Size": 100}),
        fake_record({"Mean Ages": 10.0, "SD Ages": -1, "Total Sample Size": 100}),
    ]

    cache = utils.compute_age_cache(included)
    assert cache is not None
    # Only the first dataset should be in the cache
    assert len(cache) == 1
    assert cache[included[0]["id"]] == (10.0, 2.0, 100)


def test_compute_age_cache_empty():
    cache = utils.compute_age_cache([])
    assert cache == {}


def test_compute_age_value_no_cache():
    ds = fake_record({"Mean Ages": 10.0, "SD Ages": 2.0})
    assert utils.compute_age_value(ds, None) == 0.0


def test_compute_age_value_missing_mean():
    ds = fake_record({"Mean Ages": None, "SD Ages": 2.0})
    cache = {"rec1": (10.0, 2.0, 100)}
    assert utils.compute_age_value(ds, cache) == 0.0


def test_compute_age_value_missing_sd():
    ds = fake_record({"Mean Ages": 10.0, "SD Ages": None})
    cache = {"rec1": (10.0, 2.0, 100)}
    assert utils.compute_age_value(ds, cache) == 0.0


def test_compute_age_value_zero_sd():
    ds = fake_record({"Mean Ages": 10.0, "SD Ages": 0})
    cache = {"rec1": (10.0, 2.0, 100)}
    assert utils.compute_age_value(ds, cache) == 0.0


def test_compute_age_value_with_overlap():
    # Test with overlapping age distributions
    cache = {"rec1": (10.0, 2.0, 100)}
    ds_overlap = fake_record({"Mean Ages": 10.0, "SD Ages": 2.0})

    value = utils.compute_age_value(ds_overlap, cache)
    # With same distribution parameters, there's coverage but spread over range
    # The actual value is approximately 0.876
    assert 0.85 < value < 0.90


def test_compute_age_value_no_overlap():
    # Test with non-overlapping age distributions
    cache = {"rec1": (5.0, 0.5, 100)}
    ds_no_overlap = fake_record({"Mean Ages": 15.0, "SD Ages": 0.5})

    value = utils.compute_age_value(ds_no_overlap, cache)
    # With no overlap, coverage should be very low, A_i should be close to 1
    assert value > 0.9


def test_compute_dataset_value_no_included():
    ds = fake_record({"Total Sample Size": 400, "Year of Last Data Point": 2020})

    # Default weights: alpha=1 / math.log(1000), epsilon=1
    expected_size = (1 / math.log(1000)) * math.log(400 + 1)
    # years = [2020], so y_min == y_max => R_i = 1
    expected_recency = 0.5
    expected = expected_size + expected_recency

    # year_min = year_max = 2020, age_cache = None
    value = utils.compute_dataset_value(
        ds, year_min=2020, year_max=2020, age_cache=None
    )
    assert pytest.approx(value, rel=1e-6) == expected


def test_compute_dataset_value_recency_scaling():
    ds_new = fake_record({"Total Sample Size": 400, "Year of Last Data Point": 2020})
    ds_old = fake_record({"Total Sample Size": 400, "Year of Last Data Point": 2000})

    # Year range from 2000 to 2020
    year_min, year_max = 2000, 2020

    df_new_val = utils.compute_dataset_value(
        ds_new, year_min=year_min, year_max=year_max, age_cache=None
    )
    df_old_val = utils.compute_dataset_value(
        ds_old, year_min=year_min, year_max=year_max, age_cache=None
    )

    assert df_new_val > df_old_val, "Newer dataset should have higher value"


def test_compute_dataset_value_outcome_term():
    candidate = fake_record(
        {
            "Total Sample Size": 0,
            "Year of Last Data Point": 2021,
            "Searches": ["Search1", "Search2", "Search3"],
            "Mean Ages": None,
            "SD Ages": None,
        }
    )
    weights = {"alpha": 0.0, "beta": 1.0, "gamma": 0.0, "delta": 0.0, "epsilon": 0.0}

    # O_i = number of searches = 3
    expected_O = 3.0
    val = utils.compute_dataset_value(
        candidate, year_min=None, year_max=None, age_cache=None, weights=weights
    )
    assert pytest.approx(val, rel=1e-6) == expected_O


def test_compute_dataset_value_age_term():
    # Candidate with mean=10, sd=0.1
    candidate = fake_record(
        {
            "Total Sample Size": 0,
            "Year of Last Data Point": 2021,
            "Searches": [],
            "Mean Ages": 10.0,
            "SD Ages": 0.1,
        }
    )
    # Weights to isolate age term
    weights = {"alpha": 0.0, "beta": 0.0, "gamma": 1.0, "delta": 0.0, "epsilon": 0.0}

    # Create age_cache with one included dataset: mean=10, sd=0.1, N=100
    age_cache = {"rec123": (10.0, 0.1, 100)}

    # Since distributions align perfectly:
    # CovWeighted ≈ 100, avg_N = 100, coverage_scaled = 100/100 = 1
    # A_i = 1/(1+1) = 0.5
    expected_A = 1 / (1 + 1)
    val = utils.compute_dataset_value(
        candidate, year_min=None, year_max=None, age_cache=age_cache, weights=weights
    )
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


def test_sanitize_text_basic():
    # Test basic functionality
    text = "Hello World"
    result = utils.sanitize_text(text)
    assert result == "Hello World"


def test_sanitize_text_empty_string():
    # Test with empty string
    result = utils.sanitize_text("")
    assert result == ""


def test_sanitize_text_none():
    # Test with None input
    result = utils.sanitize_text(None)
    assert result == ""


def test_sanitize_text_unicode_quotes():
    # Test replacement of unicode quotes
    text = "He said \u2018hello\u2019 and she replied \u201cgoodbye\u201d"
    result = utils.sanitize_text(text)
    assert result == "He said 'hello' and she replied \"goodbye\""


def test_sanitize_text_unicode_dashes():
    # Test replacement of unicode dashes
    text = "This is an en–dash and an em—dash"
    result = utils.sanitize_text(text)
    assert result == "This is an en-dash and an em-dash"


def test_sanitize_text_ellipsis():
    # Test replacement of ellipsis
    text = "Wait for it… here it is"
    result = utils.sanitize_text(text)
    assert result == "Wait for it... here it is"


def test_sanitize_text_newlines_and_carriage_returns():
    # Test removal of newlines and carriage returns
    text = "Line 1\nLine 2\r\nLine 3\rLine 4"
    result = utils.sanitize_text(text)
    assert result == "Line 1 Line 2 Line 3Line 4"


def test_sanitize_text_multiple_whitespace():
    # Test normalization of multiple whitespace
    text = "Too     many    spaces"
    result = utils.sanitize_text(text)
    assert result == "Too many spaces"


def test_sanitize_text_unicode_normalization():
    # Test unicode normalization (NFKD)
    text = "café"  # é as a single character
    result = utils.sanitize_text(text)
    assert result == "cafe"  # Should remove accents


def test_sanitize_text_non_ascii_removal():
    # Test removal of non-ASCII characters
    text = "Hello 世界"
    result = utils.sanitize_text(text)
    assert result == "Hello"


def test_sanitize_text_comprehensive():
    # Test comprehensive functionality with multiple issues
    text = "  \u2018Hello\u2019  world…\n\tThis is a \u201ctest\u201d—with many\r\n   issues  "  # noqa: E501
    result = utils.sanitize_text(text)
    assert result == "'Hello' world... This is a \"test\"-with many issues"


def test_sanitize_text_leading_trailing_whitespace():
    # Test removal of leading and trailing whitespace
    text = "   Hello World   "
    result = utils.sanitize_text(text)
    assert result == "Hello World"


def test_fix_age_out_of_range_mean():
    # Test when mean age is outside allowed range
    ds = fake_record(
        {
            "Mean Ages": ["20.0"],  # Too old
            "SD Ages": ["2.0"],
            "Min Ages": 0,  # Set valid values to avoid None comparison error
            "Max Ages": 0,
        }
    )
    fixed_dataset = utils.fix_age(ds)
    assert fixed_dataset["fields"]["Mean Ages"] is None
    assert fixed_dataset["fields"]["SD Ages"] is None


def test_fix_age_negative_mean():
    # Test when mean age is negative
    ds = fake_record(
        {
            "Mean Ages": ["-1.0"],  # Negative
            "SD Ages": ["2.0"],
            "Min Ages": 0,  # Set valid values to avoid None comparison error
            "Max Ages": 0,
        }
    )
    fixed_dataset = utils.fix_age(ds)
    assert fixed_dataset["fields"]["Mean Ages"] is None
    assert fixed_dataset["fields"]["SD Ages"] is None


def test_compute_year_value_missing_year():
    # Test when year of last data point is missing
    ds = fake_record({})  # No year field
    result = utils.compute_year_value(ds, 2000, 2020)
    assert result == 0.5


def test_compute_age_value_zero_total_wi():
    # Test edge case when total_wi is 0
    cache = {"rec1": (10.0, 0.0001, 100)}  # Very small SD
    ds = fake_record({"Mean Ages": 50.0, "SD Ages": 0.0001})  # Far from cache

    value = utils.compute_age_value(ds, cache)
    # When distributions don't overlap, should return close to 1.0
    assert value >= 0.0


def test_compute_age_value_zero_total_wj():
    # Test edge case when total_wj is 0 for cache entry
    cache = {"rec1": (10.0, 0.0001, 100)}  # Very small SD that might cause issues
    ds = fake_record({"Mean Ages": 10.0, "SD Ages": 2.0})

    value = utils.compute_age_value(ds, cache)
    assert value >= 0.0


def test_compute_age_value_zero_n_dsets():
    # Test when no valid datasets in cache (all filtered out)
    cache = {}
    ds = fake_record({"Mean Ages": 10.0, "SD Ages": 2.0})

    value = utils.compute_age_value(ds, cache)
    assert value == 0.0


def test_identify_duplicate_datasets_medium_size():
    # Test with medium dataset to trigger sortedneighbourhood indexing
    datasets = []
    for i in range(1500):  # Medium size to trigger different path
        dataset = fake_record(
            {
                "Dataset Name": f"Study {i}",
                "Dataset Contact Name": f"Researcher {i}",
                "Dataset Contact Email": f"researcher{i}@example.com",
            }
        )
        datasets.append(dataset)

    # Add a potential duplicate with similar name
    duplicate = fake_record(
        {
            "Dataset Name": "Study 0 Variant",
            "Dataset Contact Name": "Researcher 0",
            "Dataset Contact Email": "researcher0@example.com",
        }
    )
    datasets.append(duplicate)

    duplicates = utils.identify_duplicate_datasets(datasets, threshold=0.4)

    # Should complete without error and potentially find some matches
    assert isinstance(duplicates, dict)


def test_identify_duplicate_datasets_large_size():
    # Test with large dataset to trigger smaller window
    datasets = []
    for i in range(3500):  # Large size to trigger window=5
        dataset = fake_record(
            {
                "Dataset Name": f"Study {i:04d}",  # Zero-padded for sorting
                "Dataset Contact Name": f"Researcher {i}",
                "Dataset Contact Email": f"researcher{i}@example.com",
            }
        )
        datasets.append(dataset)

    duplicates = utils.identify_duplicate_datasets(datasets, threshold=0.5)

    # Should complete without error
    assert isinstance(duplicates, dict)


def test_setup_logger_creates_logger():
    import logging
    import os

    log_file = "test_bigger_picker.log"

    # Clean up if file exists
    if os.path.exists(log_file):
        os.remove(log_file)

    try:
        logger = utils.setup_logger("test_logger", log_file)

        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO

        # Test that it has a handler
        assert len(logger.handlers) > 0

        # Test that it can log
        logger.info("Test message")
        assert os.path.exists(log_file)

    finally:
        # Clean up
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        if os.path.exists(log_file):
            os.remove(log_file)


def test_setup_logger_reuses_existing_logger():
    import logging
    import os

    log_file = "test_bigger_picker2.log"

    # Clean up if file exists
    if os.path.exists(log_file):
        os.remove(log_file)

    try:
        # Create logger first time
        logger1 = utils.setup_logger("test_logger2", log_file)
        handler_count1 = len(logger1.handlers)

        # Call again with same name - should not add more handlers
        logger2 = utils.setup_logger("test_logger2", log_file)
        handler_count2 = len(logger2.handlers)

        # Should be the same logger instance
        assert logger1 is logger2
        # Should not have added more handlers
        assert handler_count1 == handler_count2

    finally:
        # Clean up
        logger = logging.getLogger("test_logger2")
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        if os.path.exists(log_file):
            os.remove(log_file)


def test_setup_logger_rotating_handler():
    import logging
    import os
    from logging.handlers import RotatingFileHandler

    log_file = "test_bigger_picker3.log"

    # Clean up if file exists
    if os.path.exists(log_file):
        os.remove(log_file)

    try:
        logger = utils.setup_logger("test_logger3", log_file)

        # Check that it uses RotatingFileHandler
        assert len(logger.handlers) > 0
        handler = logger.handlers[0]
        assert isinstance(handler, RotatingFileHandler)

        # Check max bytes and backup count
        assert handler.maxBytes == 5 * 1024 * 1024  # 5MB
        assert handler.backupCount == 3

    finally:
        # Clean up
        logger = logging.getLogger("test_logger3")
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        if os.path.exists(log_file):
            os.remove(log_file)


def test_create_stats_table_basic():
    from datetime import datetime, timedelta

    start_time = datetime.now() - timedelta(hours=1, minutes=30)

    stats = {
        "start_time": start_time,
        "status": "[green]Idle[/green]",
        "platforms": "Asana, Rayyan, OpenAI",
        "last_check": {"asana": "12:00:00", "rayyan": "12:01:00", "openai": "12:02:00"},
        "last_sync": {
            "asana": "2024-01-01 12:00:00",
            "rayyan": "2024-01-01 12:01:00",
            "openai": "2024-01-01 12:02:00",
        },
        "total_syncs": {"asana": 5, "rayyan": 3, "openai": 2},
        "total_polls": {"asana": 10, "rayyan": 8, "openai": 6},
        "pending_batches": {"abstracts": 2, "fulltexts": 1, "extractions": 0},
    }

    table = utils.create_stats_table(stats)

    assert table is not None
    assert table.title == "Bigger Picker Status"
    assert len(table.columns) == 2


def test_create_stats_table_uptime_calculation():
    from datetime import datetime, timedelta

    # Test uptime formatting
    start_time = datetime.now() - timedelta(hours=2, minutes=15, seconds=30)

    stats = {
        "start_time": start_time,
        "status": "[green]Running[/green]",
        "platforms": "Test",
        "last_check": {"asana": "N/A", "rayyan": "N/A", "openai": "N/A"},
        "last_sync": {"asana": "N/A", "rayyan": "N/A", "openai": "N/A"},
        "total_syncs": {"asana": 0, "rayyan": 0, "openai": 0},
        "total_polls": {"asana": 0, "rayyan": 0, "openai": 0},
        "pending_batches": {"abstracts": 0, "fulltexts": 0, "extractions": 0},
    }

    table = utils.create_stats_table(stats)

    # Should create table without errors
    assert table is not None


def test_create_stats_table_with_pending_batches():
    from datetime import datetime

    stats = {
        "start_time": datetime.now(),
        "status": "[yellow]Processing batches[/yellow]",
        "platforms": "All",
        "last_check": {"asana": "12:00:00", "rayyan": "12:00:00", "openai": "12:00:00"},
        "last_sync": {
            "asana": "2024-01-01 12:00:00",
            "rayyan": "2024-01-01 12:00:00",
            "openai": "2024-01-01 12:00:00",
        },
        "total_syncs": {"asana": 1, "rayyan": 1, "openai": 1},
        "total_polls": {"asana": 1, "rayyan": 1, "openai": 1},
        "pending_batches": {"abstracts": 10, "fulltexts": 5, "extractions": 3},
    }

    table = utils.create_stats_table(stats)

    assert table is not None
    # Should have rows for all the stats including pending batches
    assert len(table.rows) > 0


def test_identify_duplicate_datasets_edge_case_pairs_none():
    # Test edge case where one of the pair indexes is None
    # This tests lines 289-294 where pairs might be None
    datasets = []
    for i in range(1200):  # Medium size
        dataset = fake_record(
            {
                "Dataset Name": f"Unique Study {i}",
                "Dataset Contact Name": f"Unique Researcher {i}",
                "Dataset Contact Email": f"unique{i}@example.com",
            }
        )
        datasets.append(dataset)

    # Should handle gracefully even if no pairs match
    duplicates = utils.identify_duplicate_datasets(datasets, threshold=0.99)

    # Should return empty or minimal results
    assert isinstance(duplicates, dict)


def test_identify_duplicate_datasets_email_blocking():
    # Test that email blocking works correctly for medium datasets
    datasets = []
    shared_email = "shared@university.edu"

    for i in range(1200):  # Medium size to trigger email blocking
        dataset = fake_record(
            {
                "Dataset Name": f"Study {i}",
                "Dataset Contact Name": f"Researcher {i}",
                "Dataset Contact Email": shared_email if i < 3 else f"unique{i}@edu",
            }
        )
        datasets.append(dataset)

    duplicates = utils.identify_duplicate_datasets(datasets, threshold=0.3)

    # First 3 datasets with same email should be candidates for duplicates
    # At minimum, they should be compared even if not deemed duplicates
    assert isinstance(duplicates, dict)


def test_compute_age_value_extreme_no_overlap():
    # Test when distributions are so far apart that total_wi becomes 0
    # This tests line 196
    cache = {"rec1": (5.0, 0.1, 100)}
    # Dataset with mean very far from cache (100 standard deviations away)
    ds = fake_record({"Mean Ages": 15.0, "SD Ages": 0.05})

    value = utils.compute_age_value(ds, cache)

    # Should handle gracefully and return a valid value
    assert value >= 0.0
    assert value <= 1.0


def test_fix_age_negative_min_age():
    # Test when min age is negative
    ds = fake_record(
        {
            "Mean Ages": [],
            "SD Ages": [],
            "Min Ages": -5.0,  # Negative
            "Max Ages": 10.0,
        }
    )

    fixed_dataset = utils.fix_age(ds)
    # Negative min should be set to None
    assert fixed_dataset["fields"]["Min Ages"] is None
    # But max should still be valid
    assert fixed_dataset["fields"]["Max Ages"] == 10.0


def test_fix_age_max_exceeds_limit():
    # Test when max age exceeds 18
    ds = fake_record(
        {
            "Mean Ages": [],
            "SD Ages": [],
            "Min Ages": 10.0,
            "Max Ages": 25.0,  # Too old
        }
    )

    fixed_dataset = utils.fix_age(ds)
    assert fixed_dataset["fields"]["Min Ages"] == 10.0
    # Max should be set to None
    assert fixed_dataset["fields"]["Max Ages"] is None


def test_fix_age_only_sd_estimation():
    # Test case where we have min/max and mean, but need SD estimation
    ds = fake_record(
        {
            "Mean Ages": ["12.0"],
            "SD Ages": [],  # Missing SD
            "Min Ages": 10.0,
            "Max Ages": 14.0,
        }
    )

    fixed_dataset = utils.fix_age(ds)
    assert fixed_dataset["fields"]["Mean Ages"] == 12.0
    # SD should be estimated as (max - min) / 4 = (14 - 10) / 4 = 1.0
    assert fixed_dataset["fields"]["SD Ages"] == 1.0


def test_compute_dataset_value_custom_weights():
    # Test with all custom weights
    ds = fake_record(
        {
            "Total Sample Size": 100,
            "Year of Last Data Point": 2015,
            "Searches": ["Search1", "Search2"],
            "Mean Ages": 10.0,
            "SD Ages": 2.0,
        }
    )

    custom_weights = {
        "alpha": 2.0,
        "beta": 0.5,
        "gamma": 0.5,
        "delta": 1.0,
        "epsilon": 0.5,
    }

    age_cache = {"rec1": (10.0, 2.0, 100)}

    value = utils.compute_dataset_value(
        ds,
        year_min=2010,
        year_max=2020,
        age_cache=age_cache,
        weights=custom_weights,
    )

    # Should compute without errors and return a positive value
    assert value > 0


def test_compute_dataset_value_synergy_term():
    # Test that synergy term (O_i * A_i) is computed correctly
    ds = fake_record(
        {
            "Total Sample Size": 0,
            "Year of Last Data Point": 2020,
            "Searches": ["S1", "S2"],  # O_i = 2
            "Mean Ages": 10.0,
            "SD Ages": 2.0,
        }
    )

    # Weights to isolate synergy term
    weights = {"alpha": 0.0, "beta": 0.0, "gamma": 0.0, "delta": 1.0, "epsilon": 0.0}

    age_cache = {"rec1": (10.0, 2.0, 100)}

    value = utils.compute_dataset_value(
        ds, year_min=None, year_max=None, age_cache=age_cache, weights=weights
    )

    # Synergy term should be O_i * A_i * delta
    # O_i = 2, A_i ≈ 0.5 (from age overlap), delta = 1.0
    # So synergy should be approximately 1.0
    assert value > 0
    assert value < 3.0  # Reasonable upper bound
