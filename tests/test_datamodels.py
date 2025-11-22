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
        pop = Population.model_validate({
            "Age: Lower Range": 5.0,
            "Age: Upper Range": 10.0,
            "Age: Mean": 7.5,
            "Age: Standard Deviation": 1.5,
            "Sample Size: Total N": 100,
            "Sample Size: N Girls": 50,
            "Sample Size: % Girls": 50.0,
        })
        assert pop.age_lower_range == 5.0
        assert pop.age_upper_range == 10.0
        assert pop.age_mean == 7.5
        assert pop.age_sd == 1.5
        assert pop.sample_size_total == 100
        assert pop.sample_size_girls == 50
        assert pop.percent_girls == 50.0

    def test_create_with_no_fields(self):
        pop = Population()
        assert pop.age_lower_range is None
        assert pop.age_upper_range is None
        assert pop.age_mean is None
        assert pop.sample_size_total is None

    def test_alias_serialization(self):
        pop = Population.model_validate({
            "Age: Lower Range": 5.0,
            "Sample Size: Total N": 100,
        })
        dumped = pop.model_dump(by_alias=True)
        assert "Age: Lower Range" in dumped
        assert dumped["Age: Lower Range"] == 5.0
        assert "Sample Size: Total N" in dumped
        assert dumped["Sample Size: Total N"] == 100

    def test_alias_deserialization(self):
        data = {"Age: Lower Range": 5.0, "Sample Size: Total N": 100}
        pop = Population.model_validate(data)
        assert pop.age_lower_range == 5.0
        assert pop.sample_size_total == 100

    def test_json_validation(self):
        json_str = '{"Age: Lower Range": 5.0, "Sample Size: Total N": 100}'
        pop = Population.model_validate_json(json_str)
        assert pop.age_lower_range == 5.0
        assert pop.sample_size_total == 100


class TestScreenTimeMeasure:
    def test_create_with_valid_type_via_alias(self):
        stm = ScreenTimeMeasure.model_validate({
            "Screen Time Measure: Type": "Survey",
            "Screen Time Measure: Name": "Screen Time Questionnaire",
            "Types of Screen Time Measured": ["TV", "Phone"],
            "Locations of Screen Time Measured": ["Home", "School"],
        })
        assert stm.type == "Survey"
        assert stm.name == "Screen Time Questionnaire"
        assert stm.types_measured == ["TV", "Phone"]
        assert stm.locations_measured == ["Home", "School"]

    def test_valid_types(self):
        for type_val in ["Survey", "Time Use Diary", "Other"]:
            stm = ScreenTimeMeasure.model_validate({
                "Screen Time Measure: Type": type_val
            })
            assert stm.type == type_val

    def test_invalid_type_raises_error(self):
        with pytest.raises(ValidationError):
            ScreenTimeMeasure.model_validate({
                "Screen Time Measure: Type": "Invalid"
            })

    def test_alias_serialization(self):
        stm = ScreenTimeMeasure.model_validate({
            "Screen Time Measure: Type": "Survey",
            "Screen Time Measure: Name": "STQ",
        })
        dumped = stm.model_dump(by_alias=True)
        assert "Screen Time Measure: Type" in dumped
        assert dumped["Screen Time Measure: Type"] == "Survey"
        assert "Screen Time Measure: Name" in dumped

    def test_none_type_allowed(self):
        """Type is optional (None is valid)."""
        stm = ScreenTimeMeasure()
        assert stm.type is None


class TestOutcome:
    def test_create_with_all_fields_via_alias(self):
        outcome = Outcome.model_validate({
            "Outcome Group": "Learning",
            "Outcome": "Academic Achievement",
            "Outcome Measure": "Grade Point Average",
        })
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
            outcome = Outcome.model_validate({"Outcome Group": group})
            assert outcome.outcome_group == group

    def test_invalid_outcome_group_raises_error(self):
        with pytest.raises(ValidationError):
            Outcome.model_validate({"Outcome Group": "InvalidGroup"})

    def test_alias_serialization(self):
        outcome = Outcome.model_validate({
            "Outcome Group": "Learning",
            "Outcome": "Reading",
        })
        dumped = outcome.model_dump(by_alias=True)
        assert "Outcome Group" in dumped
        assert dumped["Outcome Group"] == "Learning"

    def test_none_values_allowed(self):
        """All fields are optional."""
        outcome = Outcome()
        assert outcome.outcome_group is None
        assert outcome.outcome is None


class TestArticleLLMExtract:
    def test_create_with_all_fields_via_alias(self):
        extract = ArticleLLMExtract.model_validate({
            "Corresponding Author": "Dr. Smith",
            "Corresponding Author Email": "smith@uni.edu",
            "Year of Last Data Point": 2020,
            "Study Design": "Cross-sectional",
            "Countries of Data": ["USA", "UK"],
            "Total Sample Size": 1000,
            "Dataset Name": "Smith 2020",
        })
        assert extract.corresponding_author == "Dr. Smith"
        assert extract.total_sample_size == 1000
        assert extract.study_design == "Cross-sectional"

    def test_with_nested_models(self):
        extract = ArticleLLMExtract.model_validate({
            "Corresponding Author": "Dr. Smith",
            "populations": [{"Age: Mean": 10.0}],
            "screen_time_measures": [{"Screen Time Measure: Type": "Survey"}],
            "outcomes": [{"Outcome Group": "Learning"}],
        })
        assert len(extract.populations) == 1
        assert extract.populations[0].age_mean == 10.0
        assert len(extract.screen_time_measures) == 1
        assert extract.screen_time_measures[0].type == "Survey"
        assert len(extract.outcomes) == 1
        assert extract.outcomes[0].outcome_group == "Learning"

    def test_valid_study_designs(self):
        valid_designs = ["Cross-sectional", "Longitudinal", "Experimental", "Other"]
        for design in valid_designs:
            extract = ArticleLLMExtract.model_validate({"Study Design": design})
            assert extract.study_design == design

    def test_invalid_study_design_raises_error(self):
        with pytest.raises(ValidationError):
            ArticleLLMExtract.model_validate({"Study Design": "Invalid"})

    def test_default_empty_lists(self):
        extract = ArticleLLMExtract()
        assert extract.populations == []
        assert extract.screen_time_measures == []
        assert extract.outcomes == []

    def test_alias_serialization(self):
        extract = ArticleLLMExtract.model_validate({
            "Corresponding Author": "Dr. Smith",
            "Total Sample Size": 500,
        })
        dumped = extract.model_dump(by_alias=True)
        assert "Corresponding Author" in dumped
        assert "Total Sample Size" in dumped

    def test_json_validation(self):
        json_str = '{"Corresponding Author": "Dr. Smith", "Total Sample Size": 500}'
        extract = ArticleLLMExtract.model_validate_json(json_str)
        assert extract.corresponding_author == "Dr. Smith"
        assert extract.total_sample_size == 500


class TestArticle:
    def test_inherits_from_article_llm_extract(self):
        article = Article.model_validate({
            "Corresponding Author": "Dr. Smith",
            "Rayyan ID": 12345,
            "Article Title": "Test Article",
            "Authors": "Smith, Jones",
            "Journal": "Test Journal",
            "DOI": "10.1000/xyz",
            "Year": 2020,
        })
        assert article.corresponding_author == "Dr. Smith"
        assert article.rayyan_id == 12345
        assert article.article_title == "Test Article"

    def test_alias_serialization(self):
        article = Article.model_validate({
            "Rayyan ID": 123,
            "Article Title": "Test",
            "Year": 2020,
        })
        dumped = article.model_dump(by_alias=True)
        assert "Rayyan ID" in dumped
        assert "Article Title" in dumped
        assert "Year" in dumped

    def test_search_field_as_list(self):
        article = Article.model_validate({"Search": ["SDQ", "CBCL"]})
        assert article.search == ["SDQ", "CBCL"]

    def test_all_fields_optional(self):
        article = Article()
        assert article.rayyan_id is None
        assert article.article_title is None


class TestScreeningDecision:
    def test_include_vote(self):
        decision = ScreeningDecision(
            vote="include",
            matched_inclusion=[1, 2, 3],
            rationale="All criteria met.",
        )
        assert decision.vote == "include"
        assert decision.matched_inclusion == [1, 2, 3]
        assert decision.rationale == "All criteria met."

    def test_exclude_vote(self):
        decision = ScreeningDecision(
            vote="exclude",
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
        json_str = '{"vote": "include", "rationale": "All good"}'
        decision = ScreeningDecision.model_validate_json(json_str)
        assert decision.vote == "include"
        assert decision.rationale == "All good"

    def test_model_dump(self):
        decision = ScreeningDecision(
            vote="exclude",
            triggered_exclusion=[1],
            rationale="Exclusion triggered",
        )
        dumped = decision.model_dump()
        assert dumped["vote"] == "exclude"
        assert dumped["triggered_exclusion"] == [1]
        assert dumped["rationale"] == "Exclusion triggered"
