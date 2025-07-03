from typing import Literal

from pydantic import BaseModel, Field


class Population(BaseModel):
    age_lower_range: float | None = Field(None, alias="Age: Lower Range")
    age_upper_range: float | None = Field(None, alias="Age: Upper Range")
    age_mean: float | None = Field(None, alias="Age: Mean")
    age_sd: float | None = Field(None, alias="Age: Standard Deviation")
    sample_size_total: int | None = Field(None, alias="Sample Size: Total N")
    sample_size_girls: int | None = Field(None, alias="Sample Size: N Girls")
    percent_girls: float | None = Field(None, alias="Sample Size: % Girls")


class ScreenTimeMeasure(BaseModel):
    type: Literal["Survey", "Time Use Diary", "Other"] | None = Field(
        None, alias="Screen Time Measure: Type"
    )
    name: str | None = Field(None, alias="Screen Time Measure: Name")
    types_measured: list[str] | None = Field(
        None, alias="Types of Screen Time Measured"
    )
    locations_measured: list[str] | None = Field(
        None, alias="Locations of Screen Time Measured"
    )


class Outcome(BaseModel):
    outcome_group: (
        Literal[
            "Learning", "Cognition", "Mental Health", "Behaviour", "wellbeing", "Other"
        ]
        | None
    ) = Field(None, alias="Outcome Group")
    outcome: str | None = Field(None, alias="Outcome")
    outcome_measure: str | None = Field(None, alias="Outcome Measure")


class ArticleLLMExtract(BaseModel):
    corresponding_author: str | None = Field(None, alias="Corresponding Author")
    corresponding_author_email: str | None = Field(
        None, alias="Corresponding Author Email"
    )
    year_of_last_data_point: int | None = Field(None, alias="Year of Last Data Point")
    study_design: (
        Literal["Cross-sectional", "Longitudinal", "Experimental", "Other"] | None
    ) = Field(None, alias="Study Design")
    country_of_data: list[str] | None = Field(None, alias="Countries of Data")
    total_sample_size: int | None = Field(None, alias="Total Sample Size")
    dataset_name: str | None = Field(None, alias="Dataset Name")
    # Relationships:
    populations: list[Population] = Field(default_factory=list)
    screen_time_measures: list[ScreenTimeMeasure] = Field(default_factory=list)
    outcomes: list[Outcome] = Field(default_factory=list)


class Article(ArticleLLMExtract):
    rayyan_id: int | None = Field(None, alias="Rayyan ID")
    article_title: str | None = Field(None, alias="Article Title")
    authors: str | None = Field(None, alias="Authors")
    journal: str | None = Field(None, alias="Journal")
    doi: str | None = Field(None, alias="DOI")
    year: int | None = Field(None, alias="Year")
