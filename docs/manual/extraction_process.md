# Validating Extracted Data

???+ note
    This is a somewhat convoluted process at the moment.
    We are working on improving it, and feedback is valuable.
    If you find a way something can be done better, don't keep it to yourself!

## Overview of Steps

The processing of validating extracted data is a multi-step process.
As a quick overview, the steps are:

1. Pick a dataset to validate.
2. Check the details of the article attached to the dataset.
   In particular, you need to check:
      1. The population details
      2. The screen time measure details
      3. The outcomes details (including adding a 'validated' outcome to each outcome)
3. Check the overall dataset details, including confirming that the dataset is not a duplicate.
4. Mark the dataset as 'validated' in Asana.

## Checking the Extracted Data

### Choosing a Dataset to Validate

Start by picking a dataset from the 'Awaiting Triage' set in [Asana][asana].
Even though this is also shown in Airtable, we use Asana as the 'source of truth' for the stage that a dataset is at.
Any dataset that is in the 'Awaiting Triage' set in Asana is ready to be validated.

![Asana Awaiting Triage](../imgs/asana_awaitingtriage_r.png){ width=80% }

In the 'Airtable Data' column, there is a link to the Airtable record for the dataset (highlighted in red above).
Clicking the link is the easiest way to open the Airtable record for the dataset.

### Checking the Data

There are two main ways to check the data: using the 'form' view, or using the filters.
Either is fine, but for generally checking the data I find the 'form' view easier to use.

#### Open the forms

<div class="grid cards" markdown>

- ##### 1. Open the dataset form

    ---

    If you haven't followed the link from Asana, you can open the form view by clicking the two-arrow icon that appears when you hover over a record.

    ![Step 1 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/c7cb012f-1296-4a6e-be46-fd7ae4382dd8/81a2dae3-426c-4abe-9d82-b18130583e96.png?crop=focalpoint&fit=crop&fp-x=0.1673&fp-y=0.1830&fp-z=3.0377&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=571&mark-y=351&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz01OCZoPTY4JmZpdD1jcm9wJmNvcm5lci1yYWRpdXM9MTA%3D)

- ##### 2. Open the article form

    ---

    Airtable will 'stack' forms on top of each other, which makes it quite convenient to work down through the layers of data.
    Before you can validate the dataset fields, you need to check the article.
    Clicking on the linked article (under 'Articles: IDs') will open the form for the article.

    ![Step 2 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/380d1c4c-af3f-49bb-a25f-54b6796d8310/0f92d4b8-6114-4b58-a4b4-51e6e0f1366a.png?crop=focalpoint&fit=crop&fp-x=0.4787&fp-y=0.3824&fp-z=2.0000&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=306&mark-y=542&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz01NDQmaD0xMDEmZml0PWNyb3AmY29ybmVyLXJhZGl1cz0xMA%3D%3D)

- ##### 3. Download the full text

    ---

    You'll likely want to download the full text (or open it in a new tab) so that you can view it while validating the data.

    ![Step 3 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/ce1935c9-c83a-499b-bf89-d678e39731b0/0d230073-5215-430d-af9c-79d01d22a88b.png?crop=focalpoint&fit=crop&fp-x=0.4751&fp-y=0.5612&fp-z=2.1234&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=498&mark-y=562&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz0yOSZoPTMzJmZpdD1jcm9wJmNvcm5lci1yYWRpdXM9MTA%3D)

</div>

#### Check the article form

<div class="grid cards" markdown>

- ##### 1. Check the fields on the article form

    ---

    Check the fields on the article form, such as the author details, the year of data collection, the study design, countries of data, and the total sample size.

- ##### 2. Open the hidden fields

    ---

    ![Step 4 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/6507bd26-bd74-4749-b752-e1bd2e3f5fe2/3419c354-2ec6-439f-ad4f-fc9b5dc08b30.png?crop=focalpoint&fit=crop&fp-x=0.4330&fp-y=0.9102&fp-z=1.6364&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=295&mark-y=630&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz02MTEmaD01MyZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

</div>

The next steps are to work through each of the populations, screen time measures, and outcomes in the article.

#### Check the population form(s)

<div class="grid cards" markdown>

- ##### 1. Open the population form(s)

    ---

    ![Step 5 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/9129e8cb-44c8-4c58-b8ea-41703d4064c2/cc6f7431-74e2-44de-9c15-7b9b7c254ba6.png?crop=focalpoint&fit=crop&fp-x=0.4753&fp-y=0.2612&fp-z=1.8990&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=342&mark-y=334&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz01MTYmaD05NiZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

- ##### 2. Check the population fields

    ---

    In particular, check the sample size and proportion of girls.
    Remember that you can [add][addrecord] or [remove][removerecord] populations as needed.
    Each one needs it's own record.

    ???+ tip
        Most studies will only have one population.
        Examples where you might need to have multiple populations are:

        - Studies that have split their sample by age group or gender and **not reported an 'overall' sample**.
            In this case, use a population for each group.
        - Cohort studies where there are two distinct cohorts.
            Again, if they report one overall description which covers all the participants than you can just use one population form.

- ##### 3. When you are done, close the population form

    ---

    ![Step 6 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/69b75d4d-1c36-4583-80c6-57b01c9695a3/28f81358-aea9-49dc-ac9f-d2a6da2fc0c8.png?crop=focalpoint&fit=crop&fp-x=0.5409&fp-y=0.3253&fp-z=2.0000&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=1128&mark-y=3&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz0zNyZoPTYzJmZpdD1jcm9wJmNvcm5lci1yYWRpdXM9MTA%3D)

</div>

If there are multiple populations, repeat for each one.

#### Check the screen time measure(s)

<div class="grid cards" markdown>

- ##### 1. Open the screen time measure(s)

    ---

    ![Step 7 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/1a4d28e9-11a7-4700-afdc-d5be7b9ad095/db460a50-eab4-4cb3-bf0c-8e3b549c6ddd.png?crop=focalpoint&fit=crop&fp-x=0.4753&fp-y=0.3383&fp-z=1.8990&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=342&mark-y=337&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz01MTYmaD05NiZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

- ##### 2. Check the screen time measure fields

    ---

    Remember that you can [add][addrecord] or [remove][removerecord] screen time measures if the AI has made a mistake.

    ???+ tip
        The AI tends to be quite literal when extracting here.
        For example, it might extract 'interacting on social media' because that is the term used in the article, rather than something simpler like 'social media'.
        This doesn't matter too much because we will combine these later.
        But, it can be helpful to add a simpler screen time term (like 'social media').
        Don't feel you need to spend time trying to fix the AI's extraction, though, just add an additional term if you think it will be useful.

- ##### 3. When finished, click the close button

    ---

    ![Step 8 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/48b55046-5c84-4158-ac6d-c5ce98fc159b/d652fc48-1c2e-4abe-b302-eab06e6e4fec.png?crop=focalpoint&fit=crop&fp-x=0.5461&fp-y=0.2785&fp-z=2.0000&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=1118&mark-y=74&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz0zNyZoPTYzJmZpdD1jcm9wJmNvcm5lci1yYWRpdXM9MTA%3D)

</div>

If there are multiple screen time measures, repeat for each one.

#### Check the outcome form(s)

<div class="grid cards" markdown>

- ##### 1. Open the outcome(s)

    ---

    ![Step 9 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/fb397d4a-4ad2-40a8-9559-d5bb47601ef3/4cee8f4d-bfec-4769-9a87-41e5dfa888e8.png?crop=focalpoint&fit=crop&fp-x=0.4753&fp-y=0.5749&fp-z=1.8990&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=342&mark-y=337&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz01MTYmaD05NiZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

- ##### 2. Check the outcome fields and add the validated outcome

    ---

    Start by checking the already extracted outcome fields are correct.

    ???+ tip
        You do not need to edit the **Outcome** field.
        Use this to guide you in selecting the correct validated outcome, but because of the way the AI extraction works, it is too time-consuming to fix this field.
        You should update the **Outcome Group** and the **Outcome Measure** fields, however.

- ##### 3. For each outcome add a 'validated' outcome

    ---

    You can read the full instructions for [adding a validated outcome][addvalidated] in the next section.
    Briefly, the steps are:

    1. Click the 'Add option' button.
       ![Step 19 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/ca346339-484e-4d3a-9f1e-ff41337b31de/6488691b-0962-4e52-8bf0-56bc71fe6477.png?crop=focalpoint&fit=crop&fp-x=0.3987&fp-y=0.4718&fp-z=2.8538&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=514&mark-y=332&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz0xNzMmaD01OSZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)
    2. Search for an existing matching outcome.
       If you fine one, select it and you are done.
    3. If there isn't an existing one, add a new one and complete the required fields.

- ##### 4. When finished, click the close button

</div>

If there are multiple outcomes, repeat for each one.
Remember that you can [add][addrecord] or [remove][removerecord] outcomes if the AI has made a mistake.

#### Check the dataset form

Once all of the data for the article has been checked, you can check the dataset fields.

<div class="grid cards" markdown>

- ##### 1. Check the sample size

    ---

    If you changed the sample size you should also update it in the dataset form.

    ![Step 25 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/9734c348-2b56-499c-af53-38fa646a3d7b/5dfb6664-33b1-4a32-9935-90eda82c37e6.png?crop=focalpoint&fit=crop)

- ##### 2. Check the contact name

    ---

    Check that the dataset contact name is a correctly formatted name.
    That is, remove any titles (e.g., Dr., Prof.), initials (e.g., J. Doe) and ensure it is in 'First Last' format.

    ![Step 25 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/9734c348-2b56-499c-af53-38fa646a3d7b/5dfb6664-33b1-4a32-9935-90eda82c37e6.png?crop=focalpoint&fit=crop&fp-x=0.5000&fp-y=0.5000&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=393&mark-y=640&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTMlMkNGRjc0NDImdz03MzcmaD02MiZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

- ##### 3. Check the contact email

    ---

    Check the email field matches the corresponding author email.
    If the article is quite old, a quick Google search may help to find a current email address.

    ![Step 26 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/5e3cfdee-0970-443f-981b-d7694caba4d8/8b32a51f-3d92-40cb-bdda-be707e12ef32.png?crop=focalpoint&fit=crop&fp-x=0.4603&fp-y=0.4116&fp-z=1.6869&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=304&mark-y=516&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz01OTMmaD01MCZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

- ##### 4. Check the potential duplicates

    ---

    Check the 'Potential Duplicates' field to see if there are any potential duplicates.
    If there are, follow the [deduplication instructions][dedupe] to resolve them.

    ![Step 27 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/ea76be3d-50de-435c-bcbc-a41a4c6b5c97/b21ed2f6-e7d3-42b8-9497-55d8a043cf95.png?crop=focalpoint&fit=crop&fp-x=0.2913&fp-y=0.7688&fp-z=2.0546&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=370&mark-y=531&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz00NjAmaD03MyZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

- ##### 5. Check if this is a national or government dataset

    ---

    If the dataset is a national dataset, or one that is run by a government, the recruitment process may be different.
    Use the checkbox to indicate if this is the case.

    ![Step 28 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/bffdac57-2eb6-4dd1-ae65-c87be6cbdde7/2624735b-576c-4cdb-bc9e-7f7bacdbfedb.png?crop=focalpoint&fit=crop&fp-x=0.2801&fp-y=0.8073&fp-z=2.1884&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=394&mark-y=585&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz00MTImaD04MSZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

</div>

### Updating the record in Asana

#### Checklist

When you are satisfied that the data in Airtable is correct, you can update the record in [Asana][asana] to indicate that the dataset has been validated.
Before doing this, check that you have:

- [x] Checked the dataset and article details are correct
- [x] [Removed any incorrect populations, screen time measures, or outcomes][removerecord]
- [x] [Added any additional populations, screen time measures, or outcomes][addrecord] that were not extracted by the AI
- [x] [Checked that the dataset is not a duplicate][dedupe]
- [x] Check the name and email of the corresponding author

#### Update the Asana task

???+ tip
    Make sure you use the 'Dataset ID' (e.g., `BPIPD-01`) to find the dataset in Asana.
    Don't rely on the name - it may not be unique!

<div class="grid cards" markdown>

- ##### 1. Find the dataset in Asana

    ---

    ![Step 11 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/d4d4e6a6-0271-4e60-b7b2-8e5b23febf32/9430a9c4-5498-4972-ab3b-5ec765683c29.png?crop=focalpoint&fit=crop&fp-x=0.1577&fp-y=0.5939&fp-z=1.6351&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=4&mark-y=364&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz02MTEmaD00MiZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

- ##### 2. Click on Awaiting Triage

    ---

    ![Step 12 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/4aa2bd4e-fcfa-431c-a7b3-b30f265da1ef/3a7195c3-c2a4-4943-8e33-7f1064808d5a.png?crop=focalpoint&fit=crop&fp-x=0.5074&fp-y=0.5943&fp-z=2.7740&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=499&mark-y=350&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz0yMDEmaD03MCZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

- ##### 3. Click on Validated

    ---

    ![Step 13 screenshot](https://images.tango.us/workflows/13ff0506-9759-4da9-8681-1f0d387f23a7/steps/e04835be-f6a1-49fe-a281-2e71fb07e500/7b3b41e7-7498-49f4-9882-08de486fef4d.png?crop=focalpoint&fit=crop&fp-x=0.5329&fp-y=0.6602&fp-z=2.4712&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=445&mark-y=354&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz0zMTAmaD02MyZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

    ???+ tip
        If the dataset is from some countries (e.g., China, Russia), we are unlikely to be able to access it due to Australia's Foreign Interference laws.
        In this case, you can skip 'Validated' and instead mark the dataset as 'Non-priority'.

</div>

That's it!
You have successfully validated a dataset.

[asana]: https://app.asana.com/1/653672074038961/project/1210433819516828/list/1210434509883894
[addrecord]: extraction_addremove.md/#adding-an-additional-populationscreen-time-measureoutcome
[removerecord]: extraction_addremove.md/#removing-incorrect-populationsscreen-time-measuresoutcomes
[addvalidated]: extraction_addvalidated.md/#adding-a-new-validated-outcome
[dedupe]: extraction_dedupe.md/#deduplicating-datasets
