from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Population(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age_lower_range: float | None = Field(alias="Age: Lower Range")
    age_upper_range: float | None = Field(alias="Age: Upper Range")
    age_mean: float | None = Field(alias="Age: Mean")
    age_sd: float | None = Field(alias="Age: Standard Deviation")
    sample_size_total: int | None = Field(alias="Sample Size: Total N")
    sample_size_girls: int | None = Field(alias="Sample Size: N Girls")
    percent_girls: float | None = Field(alias="Sample Size: % Girls")


class ScreenTimeMeasure(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["Survey", "Time Use Diary", "Other"] | None = Field(
        alias="Screen Time Measure: Type"
    )
    name: str | None = Field(alias="Screen Time Measure: Name")
    types_measured: list[str] | None = Field(alias="Types of Screen Time Measured")
    locations_measured: list[str] | None = Field(
        alias="Locations of Screen Time Measured"
    )


class Outcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outcome_group: (
        Literal[
            "Learning", "Cognition", "Mental Health", "Behaviour", "wellbeing", "Other"
        ]
        | None
    ) = Field(alias="Outcome Group")
    outcome: str | None = Field(alias="Outcome")
    outcome_measure: str | None = Field(alias="Outcome Measure")


class ArticleLLMExtract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    corresponding_author: str | None = Field(alias="Corresponding Author")
    corresponding_author_email: str | None = Field(alias="Corresponding Author Email")
    year_of_last_data_point: int | None = Field(alias="Year of Last Data Point")
    study_design: (
        Literal["Cross-sectional", "Longitudinal", "Experimental", "Other"] | None
    ) = Field(alias="Study Design")
    country_of_data: list[str] | None = Field(alias="Countries of Data")
    total_sample_size: int | None = Field(alias="Total Sample Size")
    dataset_name: str | None = Field(alias="Dataset Name")
    # Relationships:
    populations: list[Population]
    screen_time_measures: list[ScreenTimeMeasure]
    outcomes: list[Outcome]


class Article(ArticleLLMExtract):
    model_config = ConfigDict(extra="ignore")

    rayyan_id: int | None = Field(None, alias="Rayyan ID")
    article_title: str | None = Field(None, alias="Article Title")
    authors: str | None = Field(None, alias="Authors")
    journal: str | None = Field(None, alias="Journal")
    doi: str | None = Field(None, alias="DOI")
    year: int | None = Field(None, alias="Year")
    search: list[str] | None = Field(None, alias="Search")


class ScreeningDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vote: Literal["include", "exclude"] = Field(
        description="Final decision. Choose exactly one."
    )
    matched_inclusion: list[int] | None
    failed_inclusion: list[int] | None
    triggered_exclusion: list[int] | None
    exclusion_reasons: list[str] | None
    rationale: str
