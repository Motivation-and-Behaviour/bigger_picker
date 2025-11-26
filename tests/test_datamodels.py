"""Tests for Pydantic data models."""

import pytest
from pydantic import ValidationError

from bigger_picker.datamodels import (
    Article,
    ArticleLLMExtract,
    Outcome,
    Population,
    ScreeningDecision,
    ScreenTimeMeasure,
)


class TestPopulation:
    def test_create_with_all_fields_via_alias(self):
        """Test creating Population using alias field names (as from JSON)."""
        pop = Population.model_validate(
            {
                "Age: Lower Range": 5.0,
                "Age: Upper Range": 10.0,
                "Age: Mean": 7.5,
                "Age: Standard Deviation": 1.5,
                "Sample Size: Total N": 100,
                "Sample Size: N Girls": 50,
                "Sample Size: % Girls": 50.0,
            }
        )
        assert pop.age_lower_range == 5.0
        assert pop.age_upper_range == 10.0
        assert pop.age_mean == 7.5
        assert pop.age_sd == 1.5
        assert pop.sample_size_total == 100
        assert pop.sample_size_girls == 50
        assert pop.percent_girls == 50.0

    def test_create_with_all_fields_required(self):
        # All fields are required, test that we get validation error without them
        with pytest.raises(ValidationError):
            Population()

        # Test with all required fields provided
        pop = Population.model_validate(
            {
                "Age: Lower Range": 5.0,
                "Age: Upper Range": 10.0,
                "Age: Mean": 7.5,
                "Age: Standard Deviation": 1.5,
                "Sample Size: Total N": 100,
                "Sample Size: N Girls": 50,
                "Sample Size: % Girls": 50.0,
            }
        )
        assert pop.age_lower_range == 5.0
        assert pop.age_mean == 7.5

    def test_alias_serialization(self):
        pop = Population.model_validate(
            {
                "Age: Lower Range": 5.0,
                "Age: Upper Range": 10.0,
                "Age: Mean": 7.5,
                "Age: Standard Deviation": 1.5,
                "Sample Size: Total N": 100,
                "Sample Size: N Girls": 50,
                "Sample Size: % Girls": 50.0,
            }
        )
        dumped = pop.model_dump(by_alias=True)
        assert "Age: Lower Range" in dumped
        assert dumped["Age: Lower Range"] == 5.0
        assert "Sample Size: Total N" in dumped
        assert dumped["Sample Size: Total N"] == 100

    def test_alias_deserialization(self):
        data = {
            "Age: Lower Range": 5.0,
            "Age: Upper Range": 10.0,
            "Age: Mean": 7.5,
            "Age: Standard Deviation": 1.5,
            "Sample Size: Total N": 100,
            "Sample Size: N Girls": 50,
            "Sample Size: % Girls": 50.0,
        }
        pop = Population.model_validate(data)
        assert pop.age_lower_range == 5.0
        assert pop.sample_size_total == 100

    def test_json_validation(self):
        json_str = '{"Age: Lower Range": 5.0, "Age: Upper Range": 10.0, "Age: Mean": 7.5, "Age: Standard Deviation": 1.5, "Sample Size: Total N": 100, "Sample Size: N Girls": 50, "Sample Size: % Girls": 50.0}'  # noqa: E501
        pop = Population.model_validate_json(json_str)
        assert pop.age_lower_range == 5.0
        assert pop.sample_size_total == 100


class TestScreenTimeMeasure:
    def test_create_with_valid_type_via_alias(self):
        stm = ScreenTimeMeasure.model_validate(
            {
                "Screen Time Measure: Type": "Survey",
                "Screen Time Measure: Name": "Screen Time Questionnaire",
                "Types of Screen Time Measured": ["TV", "Phone"],
                "Locations of Screen Time Measured": ["Home", "School"],
            }
        )
        assert stm.type == "Survey"
        assert stm.name == "Screen Time Questionnaire"
        assert stm.types_measured == ["TV", "Phone"]
        assert stm.locations_measured == ["Home", "School"]

    def test_valid_types(self):
        for type_val in ["Survey", "Time Use Diary", "Other"]:
            stm = ScreenTimeMeasure.model_validate(
                {
                    "Screen Time Measure: Type": type_val,
                    "Screen Time Measure: Name": "Test Measure",
                    "Types of Screen Time Measured": ["TV"],
                    "Locations of Screen Time Measured": ["Home"],
                }
            )
            assert stm.type == type_val

    def test_invalid_type_raises_error(self):
        with pytest.raises(ValidationError):
            ScreenTimeMeasure.model_validate(
                {
                    "Screen Time Measure: Type": "Invalid",
                    "Screen Time Measure: Name": "Test Measure",
                    "Types of Screen Time Measured": ["TV"],
                    "Locations of Screen Time Measured": ["Home"],
                }
            )

    def test_alias_serialization(self):
        stm = ScreenTimeMeasure.model_validate(
            {
                "Screen Time Measure: Type": "Survey",
                "Screen Time Measure: Name": "STQ",
                "Types of Screen Time Measured": ["TV"],
                "Locations of Screen Time Measured": ["Home"],
            }
        )
        dumped = stm.model_dump(by_alias=True)
        assert "Screen Time Measure: Type" in dumped
        assert dumped["Screen Time Measure: Type"] == "Survey"
        assert "Screen Time Measure: Name" in dumped

    def test_all_fields_required(self):
        """All fields are required."""
        with pytest.raises(ValidationError):
            ScreenTimeMeasure()

        # Test with None values explicitly provided
        stm = ScreenTimeMeasure.model_validate(
            {
                "Screen Time Measure: Type": None,
                "Screen Time Measure: Name": None,
                "Types of Screen Time Measured": None,
                "Locations of Screen Time Measured": None,
            }
        )
        assert stm.type is None


class TestOutcome:
    def test_create_with_all_fields_via_alias(self):
        outcome = Outcome.model_validate(
            {
                "Outcome Group": "Learning",
                "Outcome": "Academic Achievement",
                "Outcome Measure": "Grade Point Average",
            }
        )
        assert outcome.outcome_group == "Learning"
        assert outcome.outcome == "Academic Achievement"
        assert outcome.outcome_measure == "Grade Point Average"

    def test_valid_outcome_groups(self):
        valid_groups = [
            "Learning",
            "Cognition",
            "Mental Health",
            "Behaviour",
            "wellbeing",
            "Other",
        ]
        for group in valid_groups:
            outcome = Outcome.model_validate(
                {
                    "Outcome Group": group,
                    "Outcome": "Test Outcome",
                    "Outcome Measure": "Test Measure",
                }
            )
            assert outcome.outcome_group == group

    def test_invalid_outcome_group_raises_error(self):
        with pytest.raises(ValidationError):
            Outcome.model_validate(
                {
                    "Outcome Group": "InvalidGroup",
                    "Outcome": "Test Outcome",
                    "Outcome Measure": "Test Measure",
                }
            )

    def test_alias_serialization(self):
        outcome = Outcome.model_validate(
            {
                "Outcome Group": "Learning",
                "Outcome": "Reading",
                "Outcome Measure": "Reading Test Score",
            }
        )
        dumped = outcome.model_dump(by_alias=True)
        assert "Outcome Group" in dumped
        assert dumped["Outcome Group"] == "Learning"

    def test_all_fields_required(self):
        """All fields are required."""
        with pytest.raises(ValidationError):
            Outcome()

        # Test with None values explicitly provided
        outcome = Outcome.model_validate(
            {"Outcome Group": None, "Outcome": None, "Outcome Measure": None}
        )
        assert outcome.outcome_group is None
        assert outcome.outcome is None


class TestArticleLLMExtract:
    def test_create_with_all_fields_via_alias(self):
        extract = ArticleLLMExtract.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA", "UK"],
                "Total Sample Size": 1000,
                "Dataset Name": "Smith 2020",
                "populations": [],
                "screen_time_measures": [],
                "outcomes": [],
            }
        )
        assert extract.corresponding_author == "Dr. Smith"
        assert extract.total_sample_size == 1000
        assert extract.study_design == "Cross-sectional"

    def test_with_nested_models(self):
        extract = ArticleLLMExtract.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA"],
                "Total Sample Size": 1000,
                "Dataset Name": "Smith 2020",
                "populations": [
                    {
                        "Age: Lower Range": 5.0,
                        "Age: Upper Range": 15.0,
                        "Age: Mean": 10.0,
                        "Age: Standard Deviation": 2.0,
                        "Sample Size: Total N": 100,
                        "Sample Size: N Girls": 50,
                        "Sample Size: % Girls": 50.0,
                    }
                ],
                "screen_time_measures": [
                    {
                        "Screen Time Measure: Type": "Survey",
                        "Screen Time Measure: Name": "Test Survey",
                        "Types of Screen Time Measured": ["TV"],
                        "Locations of Screen Time Measured": ["Home"],
                    }
                ],
                "outcomes": [
                    {
                        "Outcome Group": "Learning",
                        "Outcome": "Reading",
                        "Outcome Measure": "Reading Score",
                    }
                ],
            }
        )
        assert len(extract.populations) == 1
        assert extract.populations[0].age_mean == 10.0
        assert len(extract.screen_time_measures) == 1
        assert extract.screen_time_measures[0].type == "Survey"
        assert len(extract.outcomes) == 1
        assert extract.outcomes[0].outcome_group == "Learning"

    def test_valid_study_designs(self):
        valid_designs = ["Cross-sectional", "Longitudinal", "Experimental", "Other"]
        for design in valid_designs:
            extract = ArticleLLMExtract.model_validate(
                {
                    "Corresponding Author": "Dr. Smith",
                    "Corresponding Author Email": "smith@uni.edu",
                    "Year of Last Data Point": 2020,
                    "Study Design": design,
                    "Countries of Data": ["USA"],
                    "Total Sample Size": 1000,
                    "Dataset Name": "Smith 2020",
                    "populations": [],
                    "screen_time_measures": [],
                    "outcomes": [],
                }
            )
            assert extract.study_design == design

    def test_invalid_study_design_raises_error(self):
        with pytest.raises(ValidationError):
            ArticleLLMExtract.model_validate(
                {
                    "Corresponding Author": "Dr. Smith",
                    "Corresponding Author Email": "smith@uni.edu",
                    "Year of Last Data Point": 2020,
                    "Study Design": "Invalid",
                    "Countries of Data": ["USA"],
                    "Total Sample Size": 1000,
                    "Dataset Name": "Smith 2020",
                    "populations": [],
                    "screen_time_measures": [],
                    "outcomes": [],
                }
            )

    def test_all_fields_required(self):
        # Test that all fields are required
        with pytest.raises(ValidationError):
            ArticleLLMExtract()

        # Test with all required fields
        extract = ArticleLLMExtract.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA"],
                "Total Sample Size": 1000,
                "Dataset Name": "Smith 2020",
                "populations": [],
                "screen_time_measures": [],
                "outcomes": [],
            }
        )
        assert extract.populations == []
        assert extract.screen_time_measures == []
        assert extract.outcomes == []

    def test_alias_serialization(self):
        extract = ArticleLLMExtract.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA"],
                "Total Sample Size": 500,
                "Dataset Name": "Smith 2020",
                "populations": [],
                "screen_time_measures": [],
                "outcomes": [],
            }
        )
        dumped = extract.model_dump(by_alias=True)
        assert "Corresponding Author" in dumped
        assert "Total Sample Size" in dumped

    def test_json_validation(self):
        json_str = '{"Corresponding Author": "Dr. Smith", "Corresponding Author Email": "smith@uni.edu", "Year of Last Data Point": 2020, "Study Design": "Cross-sectional", "Countries of Data": ["USA"], "Total Sample Size": 500, "Dataset Name": "Smith 2020", "populations": [], "screen_time_measures": [], "outcomes": []}'  # noqa: E501
        extract = ArticleLLMExtract.model_validate_json(json_str)
        assert extract.corresponding_author == "Dr. Smith"
        assert extract.total_sample_size == 500


class TestArticle:
    def test_inherits_from_article_llm_extract(self):
        article = Article.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA"],
                "Total Sample Size": 1000,
                "Dataset Name": "Smith 2020",
                "populations": [],
                "screen_time_measures": [],
                "outcomes": [],
                "Rayyan ID": 12345,
                "Article Title": "Test Article",
                "Authors": "Smith, Jones",
                "Journal": "Test Journal",
                "DOI": "10.1000/xyz",
                "Year": 2020,
            }
        )
        assert article.corresponding_author == "Dr. Smith"
        assert article.rayyan_id == 12345
        assert article.article_title == "Test Article"

    def test_alias_serialization(self):
        article = Article.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA"],
                "Total Sample Size": 1000,
                "Dataset Name": "Smith 2020",
                "populations": [],
                "screen_time_measures": [],
                "outcomes": [],
                "Rayyan ID": 123,
                "Article Title": "Test",
                "Year": 2020,
            }
        )
        dumped = article.model_dump(by_alias=True)
        assert "Rayyan ID" in dumped
        assert "Article Title" in dumped
        assert "Year" in dumped

    def test_search_field_as_list(self):
        article = Article.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA"],
                "Total Sample Size": 1000,
                "Dataset Name": "Smith 2020",
                "populations": [],
                "screen_time_measures": [],
                "outcomes": [],
                "Search": ["SDQ", "CBCL"],
            }
        )
        assert article.search == ["SDQ", "CBCL"]

    def test_inherited_fields_required(self):
        # Test that inherited fields from ArticleLLMExtract are required
        with pytest.raises(ValidationError):
            Article()

        # Test with all required fields from parent class
        article = Article.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA"],
                "Total Sample Size": 1000,
                "Dataset Name": "Smith 2020",
                "populations": [],
                "screen_time_measures": [],
                "outcomes": [],
            }
        )
        # Article-specific fields have defaults
        assert article.rayyan_id is None
        assert article.article_title is None


class TestScreeningDecision:
    def test_include_vote(self):
        decision = ScreeningDecision(
            vote="include",
            matched_inclusion=[1, 2, 3],
            failed_inclusion=None,
            triggered_exclusion=None,
            exclusion_reasons=None,
            rationale="All criteria met.",
        )
        assert decision.vote == "include"
        assert decision.matched_inclusion == [1, 2, 3]
        assert decision.rationale == "All criteria met."

    def test_exclude_vote(self):
        decision = ScreeningDecision(
            vote="exclude",
            matched_inclusion=None,
            failed_inclusion=[1],
            triggered_exclusion=[2],
            exclusion_reasons=["No screen time measure"],
            rationale="Failed inclusion criterion 1.",
        )
        assert decision.vote == "exclude"
        assert decision.failed_inclusion == [1]
        assert decision.triggered_exclusion == [2]

    def test_invalid_vote_raises_error(self):
        with pytest.raises(ValidationError):
            ScreeningDecision(vote="maybe", rationale="Unsure")

    def test_rationale_required(self):
        with pytest.raises(ValidationError):
            ScreeningDecision(vote="include")

    def test_json_validation(self):
        json_str = '{"vote": "include", "matched_inclusion": [1, 2], "failed_inclusion": null, "triggered_exclusion": null, "exclusion_reasons": null, "rationale": "All good"}'  # noqa: E501
        decision = ScreeningDecision.model_validate_json(json_str)
        assert decision.vote == "include"
        assert decision.rationale == "All good"

    def test_model_dump(self):
        decision = ScreeningDecision(
            vote="exclude",
            matched_inclusion=None,
            failed_inclusion=None,
            triggered_exclusion=[1],
            exclusion_reasons=None,
            rationale="Exclusion triggered",
        )
        dumped = decision.model_dump()
        assert dumped["vote"] == "exclude"
        assert dumped["triggered_exclusion"] == [1]
        assert dumped["rationale"] == "Exclusion triggered"
