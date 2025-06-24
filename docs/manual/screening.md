# Screening

## Overview

The purpose of screening is to identify articles that contain datasets relevant to the Bigger Picture project.
This process involves two main steps:

1. **Title and Abstract Screening**: Initial screening of articles based on their titles and abstracts to remove completely irrelevant articles.
2. **Full Text Screening**: A more detailed review of the full text of articles that passed the initial screening to determine if they contain relevant datasets.

The below outlines the process for screening articles, and the criteria we use to determine whether an article is relevant to the Bigger Picture project.

## Setup

To begin screening, you will need access to [Rayyan](https://www.rayyan.ai/) and the [Bigger Picture Project](https://new.rayyan.ai/reviews/1388927/overview).
If you don't have access, please let Taren know.

## Inclusion and Exclusion Criteria

The below are the criteria that we use to assess whether an article is relevant to the Bigger Picture project.
You should read these carefully before beginning the screening process.
Note that you can also access these criteria in Rayyan by clicking the ![Rayyan Criteria Icon](../imgs/rayyan_criteria.png) icon in the top right corner of the screen.

???+ tip
    You can also press the ++c++ key to open the criteria in Rayyan.

=== "Inclusion Criteria"

    --8<-- "assets/inclusion_exclusion_criteria.md:inclusion"

=== "Exclusion Criteria"

    --8<-- "assets/inclusion_exclusion_criteria.md:exclusion"

## Screening Process

We are only screening articles once, rather than screening in duplicate as is common in systematic reviews.
We may later go back and double-screen articles that were excluded to ensure we haven't missed anything, but our priority is to get through the screening process as quickly as possible so that we can start contacting authors.
When screening in Rayyan, it is important to set the filters so that you are only seeing articles that have not been screened yet, as this is not the default.

### Title and Abstract Screening

The goal of the title and abstract stage is just to remove articles that are clearly irrelevant to the Bigger Picture project.
We aim to do this bit as quickly as possible - don't labour over decisions at this stage.
If you are on the fence about an article, it is best to include it and review it in the full text stage.

#### Setup Rayyan for Title and Abstract Screening

1. Log in to [Rayyan](https://www.rayyan.ai/) and navigate to the [Bigger Picture Project](https://new.rayyan.ai/reviews/1388927/overview).
2. Click on the **Screening** tab.
3. Set the filters to show only articles that need to be screened:
      - The filter by inclusion at the top of the list of articles should be set to 'Undecided':

        ![Rayyan Undecided Filter](../imgs/rayyan_undecided.png)

      - The 'Max member Decisions' filter should be set to 'At most 0' (that is, articles that have not been screened by anyone yet):

        ![Rayyan Max Member Decisions Filter](../imgs/rayyan_max_decisions.png)

You are welcome to use the other filters to speed up the process.
Some useful filters are:

- *Keywords for Include/Exclude*: These are words that we have identified as common in either articles that are usually included or excluded.

#### Screening Title and Abstracts

Use the ![Rayyan Include](../imgs/rayyan_include.png) or ![Rayyan Exclude](../imgs/rayyan_exclude.png) buttons to screen articles.
Avoid using the ![Rayyan Maybe](../imgs/rayyan_maybe.png) button, as this just requires it to be screened again later.

The fastest way to screen articles is to use the keyboard shortcuts in Rayyan.
Use the ++i++ key to include an article, the ++e++ key to exclude it.

???+ tip
    You can quickly view the keyboard shortcuts in Rayyan by pressing the ++v++ key.

### Full Text Screening

#### Setup Rayyan for Full Text Screening

Setting up Rayyan is the same as for [Title and Abstract Screening](#setup-rayyan-for-title-and-abstract-screening).
Navigate to the **Full Text Screening** tab and apply the same filters as above.
You may also want to filter by if an article already has a PDF attached by setting the 'Full Text' filter to 'Private' (:person_shrugging:).

#### Screening Full Texts

There are two main differences between the full text screening and the title and abstract screening:

<div class="annotate" markdown>

1. When you exclude an article, you need to provide a reason.
   You do this using the 'Exclude with Reasons' box at the bottom of the screen.

    ???+ tip
        You can quickly access the exclusion reasons by pressing the ++r++ key.

2. When you include an article, you need to add a label that tells our software that it is ready to be extracted. (1)
   When you have included an article,

</div>

1. For some inexplicable reason, the Rayyan API does not differentiate between articles included at the title and abstract stage and those included at the full text stage.
   So, we have to use a label to indicate that an article is ready for extraction.

## Other Useful Information

### Rayyan Ratings

### Potentially Relevant Systematic Reviews

### Rayyan Tips and Tricks
