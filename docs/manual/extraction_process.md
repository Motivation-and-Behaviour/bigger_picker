# Validating Extracted Data

???+ note
    This is a somewhat convoluted process at the moment.
    We are working on improving it, and feedback is valuable.
    If you find a way something can be done better, don't keep it to yourself!

## Checking the Extracted Data

Start by picking a dataset from the 'Needs Validation' set in Asana.
Even though this is also shown in Airtable, we use Asana as the 'source of truth' for the stage that a dataset is at.
In the 'Airtable Data' column, there is a link to the Airtable record for the dataset.
![Airtable Link](../imgs/asana_airtable_link.png)
Clicking the link is the easiest way to open the Airtable record for the dataset.

```mermaid
flowchart TD
    Dataset["Dataset"]
    Article["Articles"]
    Population["Populations"]
    ScreenTime["Screen Time Measures"]
    Outcome["Outcomes"]

    Dataset -->|can have many| Article
    Article -->|can have many| Population
    Article -->|can have many| ScreenTime
    Article -->|can have many| Outcome
```
