# _______RAYYAN_________
RAYYAN_REVIEW_ID = 1388927
RAYYAN_LABELS = {
    "unextracted": "Included: Not Yet Extracted",
    "extracted": "Included: AI Extracted",
    "included": "BP: Included",
    "excluded": "BP: Excluded",
}
RAYYAN_EXCLUSION_LABELS = [
    "__EXR__wrong age",
    "__EXR__wrong study design",
    "__EXR__Wrong screen time measurement ",
    "__EXR__wrong outcome",
    "__EXR__data not available",
    "__EXR__foreign language",
    "__EXR__Not focused on screen time.",
    "__EXR__wrong publication type",
    "__EXR__wrong population",
    "__EXR__background article",
]

# _______AIRTABLE_________
AIRTABLE_BASE_ID = "appYuP4DjRt023FK1"
AIRTABLE_TABLE_IDS = {
    "Datasets": "tblF59g2CmrQhsoVW",
    "Articles": "tblXA2a46D7dTX0Gg",
    "Populations": "tblftmMN6HlT7hhd8",
    "Screen Time Measures": "tblVnxnPP2CofEsBt",
    "Outcomes": "tbl9oOmISnYmwDwlV",
}
AIRTABLE_DEFAULT_VIEW_ID = "viwkrTb1IADMvI6eg"

# _______ASANA_________
ASANA_PROJECT_ID = "1210433819516828"
ASANA_CUSTOM_FIELD_IDS = {
    "BPIPD": "1210434574043335",
    "Status": "1210433819516835",
    "Dataset Value": "1210433819516841",
    "Data Sharing Method": "1210468704477537",
    "Airtable Data": "1210433819516843",
    "Searches": "1211763557587634",
}
ASANA_STATUS_ENUM_VALUES = {
    "Awaiting Triage": "1210433819516836",
    "Validated": "1210528062577747",
    "Non-priority": "1210433819516837",
    "Mail Merge": "1211763557587633",
    "Contacting Authors": "1210433819516838",
    "Agreed & Awaiting Data": "1210468704477552",
    "Included": "1210433819516839",
    "Declined": "1210468704477553",
}
ASANA_SEARCHES_ENUM_VALUES = {
    "SDQ": "1211763557587635",
}
# _______OPENAI_________
STUDY_OBJECTIVES = """
The objective of this review is to identify studies with datasets which can be included in an individual participant data (IPD) meta-analysis on children's screen time and its impact on learning, mental health, wellbeing, and behaviour.
"""  # noqa: E501

INCLUSION_HEADER = """
The following is an excerpt of 2 sets of criteria. A study is considered included if it meets all the inclusion criteria. If a study meets any of the exclusion criteria, it should be excluded. Here are the 2 sets of criteria:
"""  # noqa: E501

INCLUSION_CRITERIA = [
    "Children and adolescents <18 years of age. Include studies with a mean sample age younger than 18 years. If a mean study age is not available, we will use the midpoint of the age range.",  # noqa: E501
    "Cross-sectional, longitudinal studies, or control groups from experimental studies",  # noqa: E501
    "Studies must report quantitative screen time exposure that is disaggregated by factors such as device or activity type (e.g., time spent on social media, time spent on smartphones, time spent watching tv, time spent on schoolwork or educational content, watching vs interactive use), and not just a report a single aggregated 'total screen time value'. The goal is to understand how screen time is being used, not just how much is being used. Studies will be included if disaggregated screen time data was collected, even if only aggregated results were reported.",  # noqa: E501
    "Quantitative measurement of at least one outcome related to children's learning, cognitive abilities, mental health, wellbeing, or behaviour. Examples include: (i) Learning: General education, numeracy, literacy; (ii) Cognitive abilities: Executive function, cognitive function; (iii) Mental health: Anxiety, Depression, Emotions; (iv) Behaviour: Aggression, Self-regulation, Prosocial behaviour; (v) Wellbeing: Self-perceptions, Quality of life, Life satisfaction, Self-efficacy",  # noqa: E501
]

EXCLUSION_CRITERIA = [
    "Adults > 18 years of age. Exclude studies with a mean sample age older than 18 years. If the mean age is unclear, then exclude if the midpoint of the age range is greater than 18 years.",  # noqa: E501
    "Studies that do not have a quantitative design, including reviews (systematic reviews, meta-analysis, literature reviews); correspondences; case reports, case series or case studies with no participant-level quantitative data; qualitative-only designs; studies that only report group-level associations (e.g., screen use rates and test scores by country).",  # noqa: E501
    "Independent Variables: (i) Only measured total or aggregated screen time (i.e., total screen time) without distinction between content or type. Furthermore, no disaggregated screen time data was collected; (ii) Does not specify the type of screen activity (e.g., TV, social media, video games) and/or content (e.g., educational vs. recreational); (iii) Only measured 'problematic screen use' (e.g., internet addiction scales) which do not provide time-based measurements.",  # noqa: E501
    "Does not include at least one quantitatively measured outcome related to learning, cognitive abilities, mental health, wellbeing, or behaviour.",  # noqa: E501
    "Data availability statement states that data cannot be shared. This may be stated in the data availability section in the full-text.",  # noqa: E501
    "Full-text not available in English",  # noqa: E501
]

SCREENING_INSTRUCTIONS = """
We now assess whether the paper should be included from the systematic review by evaluating it against each and every predefined inclusion and exclusion criterion. First, we will reflect on how we will decide whether a paper should be included or excluded. Then, we will think step by step for each criteria, giving reasons for why they are met or not met.
Follow the schema exactly:
- Use 1-based indices for criteria lists.
- If none apply, return an empty list [] for any list field.
- 'triggered_exclusion' and 'exclusion_reasons' must align in order and length.
- 'rationale' should be a short paragraph (3-6 sentences) and must not exceed 1000 characters."""  # noqa: E501

ARTICLE_EXTRACTION_PROMPT = """ 
You are an experienced research assistant supporting a systematic review of academic studies on children's screen time and its outcomes.
These systematic reviews will be used to inform an individual participant data (IPD) meta-analysis.
Your task is to read the provided academic article (in PDF form) and extract key study characteristics and results, using your best judgment and caution.

Important:
- If information for a field is not reported, is ambiguous, or you are not confident you have interpreted it correctly, leave that field blank (`null` in JSON) or as an empty list.
- Only extract what is clearly stated or can be deduced with high confidence from the article.
- Do **not** infer or guess missing information beyond what is directly supported by the text, tables, or figures.

Return your answer into the given structure.
The below information helps describe the information to look for for each field.

Field-by-Field Guidance

Article-Level Fields
- "Corresponding Author": The name of the corresponding author. Look for author lists, footnotes, or contact information sections.
- "Corresponding Author Email": The email address for the corresponding author, usually found in the author affiliations or correspondence section.
- "Year of Last Data Point": The year when the last data point was collected in the study. This is often found in the Methods or Results sections, or in the discussion of the study timeline.
- "Study Design": The type of study design used in the research. Choose from:
  - "Cross-sectional": Data collected at one point in time.
  - "Longitudinal": Data collected over multiple time points.
  - "Experimental": Involves manipulation of variables (e.g., randomized controlled trials).
  - "Other": If the design does not fit the above categories, specify the design.
- "Countries of Data": A list of countries where the data was collected. This is often found in the Methods section or in the author affiliations. Note that it could be different to the affiliation of the authors.
- "Total Sample Size": The total number of participants in the study, which is often reported in the Methods or Results sections, or in Table 1.
- "Dataset Name": The name of the dataset used in the study, if specified. This may be mentioned in the Methods section or in the data availability statement.

Populations (list of population groups, under "populations")
For each distinct population or participant group described in the study, extract:
- "Age: Lower Range": The minimum reported age of participants (e.g., “participants aged 8-12” would mean that the lower range is 8).
- "Age: Upper Range": The maximum reported age of participants.
- "Age: Mean": The average (mean) age, if provided.
- "Age: Standard Deviation": The standard deviation of the age, if provided.
- "Sample Size: Total N": The total number of participants in the group.
- "Sample Size: N Girls": The number of female participants, if reported.
- "Sample Size: % Girls": The percentage of female participants, if reported. Enter the percentage of female participants as a decimal between 0 and 1 (e.g., 0.471 for 47.1%). Do **not** enter raw counts or numbers greater than 1. If a percentage is reported (e.g., 47.1%), divide by 100.
Tip: This information is often in the “Participants” or “Sample” section, or in Table 1.

Screen Time Measures (list of measures, under "screen_time_measures")
For each distinct way that screen time was measured or operationalized, extract:
- "Screen Time Measure: Type": Select only one of "Survey", "Diary", or "Other".
  - "Survey": A questionnaire or self-report instrument.
  - "Diary": Participants kept a record or log of their activities, and these included screen time. Will sometimes be called a 'Time Use Diary'.
  - "Other": Any other type of measure (specify the method in the “Name” field).
- "Screen Time Measure: Name": The specific name of the measure or instrument (e.g., "ScreenQ", "Custom Survey"), if reported. If they used a custom survey they may not give it a specific name, so you can use 'Custom Survey'.
- "Types of Screen Time Measured": A list of all types of screen use captured by the measure (e.g., "TV", "Computer", "Smartphone", "Video Games"), if specified.
- "Locations of Screen Time Measured": A list of physical locations (e.g., "School", "Home") where screen time was assessed, if reported. If it seems as though they just measured overall screen time without specifiying locations, you can use "General".
Tip: This information is typically in the Methods section, Measures subsection, or in tables describing data collection.

Outcomes (list, under "outcomes")
For each outcome or endpoint reported in relation to screen time, extract:
- "Outcome Group": Choose only from the following categories:
  "Learning", "Cognition", "Mental Health", "Behaviour", "wellbeing", "Other".
  - Select the category that best fits the outcome described in the study.
  - Use "Other" only if none of the main categories are appropriate.
- "Outcome": The name that would be given to the outcome measured (e.g., "Academic Achievement", "Anxiety", "Physical Aggression").
- "Outcome Measure": The name of the tool or scale used to assess the outcome (e.g., "WISC-IV", "CBCL Anxiety Subscale", "Teacher Report").
Tip: Look for these in the Methods, Results, or Supplementary sections, or in tables summarizing outcome variables.

General Instructions
- Only include one set of "corresponding_author" and "corresponding_author_email" at the article level.
- Each list (populations, screen time measures, outcomes) may have one or more entries, or be empty if the information is not available.
- Leave any field as null or blank if you are not confident in the extraction.

If a field is not reported or cannot be determined with confidence, set its value to null or leave it blank/empty.
Be thorough, cautious, and prioritize precision and reliability over guesswork.
"""  # noqa: E501
# _______RENDER_________
RENDER_WEBHOOK_URL = "https://bigger-picker.onrender.com/webhook"
