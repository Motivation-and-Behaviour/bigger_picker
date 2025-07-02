# Deduplicating Datasets

## Rationale

Since our primary method of finding datasets is via published articles, it is inevitable that we will end up with some articles that use the same dataset.
This is not a problem, but we want to merge these so that each dataset we are tracking is unique.

## Identifying Duplicate Datasets

We mark potential duplicate datasets in the 'Possible Duplicates' field in Airtable.
These are links to other datasets that match on one or many fields, such as the dataset name or the dataset contact.
These are only an indication though, and it is worth checking if there are other potential duplicates that need to be merged.

Some other methods to identify duplicates include:

- Sorting the datasets table by the Dataset Contact Name, or the the Dataset Name.
- Searching using either the filter or the 'Find in View' feature.
  This is useful for checking names, as sometimes the title of the contact is included (e.g., "Dr. John Smith"), which means that sorting by the contact name will not work.

???+ tip
    One other common way to have a duplicate is in the case of longitudinal study designs.
    It is common for longitudinal studies to report on baseline results, and separately on longitudinal results.
    In general, the longitudinal dataset is the one we want to keep, as it includes the baseline data.

## Overview of Steps

Once you have identified that a dataset is a duplicate, you will need to go through the steps of deduplicating it.
The full process is below, but the general steps are:

1. Validate the articles on both datasets (and the outcomes, etc)
2. Pick one dataset to be the "main" dataset.
   We will call the other dataset the "duplicate" dataset.
3. On the "main" dataset, add the article referenced in the "duplicate" dataset using the article ID.
   This will automatically add the populations, screen time measures, and outcomes from the "duplicate" dataset.
4. Check the fields on the "main" dataset to see if they need to be updated.
   For example, the contact person may need to be updated, or the total sample size may be changed.
5. In Airtable, delete the "duplicate" dataset.
6. In Asana, delete the "duplicate" dataset task.

## Deduplicating a Dataset

For the below example, I'll be deduplicating these two datasets.
Throughout the process, I will refer to the dataset with the ID `BPIPD-92` as the **^^main^^** dataset, and the dataset with the ID `BPIPD-39` as the **^^duplicate^^** dataset.

![Step 1 screenshot](https://images.tango.us/workflows/d4e6501a-c2cf-4145-b224-ea1eda6ce403/steps/4550060f-93c6-44b1-87f8-458f9e772847/eb9a5c43-36c5-4530-9b1c-49d47b4257b3.png?crop=focalpoint&fit=crop&fp-x=0.5000&fp-y=0.5000&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=50&mark-y=513&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTMlMkNGRjc0NDImdz0xMTA5Jmg9NTYmZml0PWNyb3AmY29ybmVyLXJhZGl1cz0xMA%3D%3D)

### [Airtable](https://airtable.com/appYuP4DjRt023FK1) Steps

#### Get the Article ID of the ^^duplicate^^ dataset

<div class="grid" markdown>

Click on the Article ID of the ^^duplicate^^ dataset

![Step 1 screenshot](https://images.tango.us/workflows/d4e6501a-c2cf-4145-b224-ea1eda6ce403/steps/4550060f-93c6-44b1-87f8-458f9e772847/98a76f82-8898-4f43-9ff0-a0167d1b627c.png?crop=focalpoint&fit=crop&fp-x=0.7222&fp-y=0.5200&fp-z=2.0883&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=863&mark-y=442&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz0xMTkmaD01MCZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

Copy the Article ID.
This is easier than trying to type it out.

![Step 2 screenshot](https://images.tango.us/workflows/d4e6501a-c2cf-4145-b224-ea1eda6ce403/steps/7783d673-45e3-4e8e-91d2-9b736774ff33/8e517f53-5b63-488c-8632-dd8def162f39.png?crop=focalpoint&fit=crop&fp-x=0.3945&fp-y=0.1893&fp-z=1.3454&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=242&mark-y=231&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz03MTYmaD01MiZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

Then close the form.

![Step 3 screenshot](https://images.tango.us/workflows/d4e6501a-c2cf-4145-b224-ea1eda6ce403/steps/8ffaeabe-0913-4bb7-9e48-8a064d99f200/6c2b3ea9-a696-4528-bd0d-6e36c698a826.png?crop=focalpoint&fit=crop&fp-x=0.8498&fp-y=0.1030&fp-z=2.9090&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=638&mark-y=238&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz03NSZoPTEyOCZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

</div>

#### Add the Article ID to the ^^main^^ dataset

<div class="grid" markdown>

Open the form for the ^^main^^ dataset.

![Step 4 screenshot](https://images.tango.us/workflows/d4e6501a-c2cf-4145-b224-ea1eda6ce403/steps/6151c085-fb02-4d17-a22d-2b0a32815d08/e6a7a386-e41e-41f4-ab5c-f47e38fce3df.png?crop=focalpoint&fit=crop&fp-x=0.0821&fp-y=0.4773&fp-z=3.0726&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=263&mark-y=464&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz03OSZoPTc5JmZpdD1jcm9wJmNvcm5lci1yYWRpdXM9MTA%3D)

Click the "Add Article" button.

![Step 5 screenshot](https://images.tango.us/workflows/d4e6501a-c2cf-4145-b224-ea1eda6ce403/steps/33670a03-226b-4654-8c38-79c142f2e33b/d9a75ae2-efa3-49ef-ba88-bbce7fc9c3e2.png?crop=focalpoint&fit=crop&fp-x=0.3298&fp-y=0.6142&fp-z=2.7167&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=489&mark-y=464&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz0yMjImaD03OCZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

Paste the Article ID into the search.

![Step 6 screenshot](https://images.tango.us/workflows/d4e6501a-c2cf-4145-b224-ea1eda6ce403/steps/0362fbd7-ab01-45fe-8dcb-484c7fc5500b/481023c5-91bd-4e91-b97f-0cebd95142d2.png?crop=focalpoint&fit=crop&fp-x=0.4866&fp-y=0.6508&fp-z=1.5264&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=275&mark-y=479&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz02NTAmaD00OSZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

The article from the ^^duplicate^^ dataset should appear.
You can then select it to add it to the ^^main^^ dataset.

![Step 7 screenshot](https://images.tango.us/workflows/d4e6501a-c2cf-4145-b224-ea1eda6ce403/steps/9fe27167-cb00-4e4b-9940-ea73b3bbbe6d/fce4d5fa-374d-4116-a286-e741302eee16.png?crop=focalpoint&fit=crop&fp-x=0.4987&fp-y=0.6874&fp-z=1.4199&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=254&mark-y=476&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz02OTImaD0xNjgmZml0PWNyb3AmY29ybmVyLXJhZGl1cz0xMA%3D%3D)

Then close the form.

![Step 8 screenshot](https://images.tango.us/workflows/d4e6501a-c2cf-4145-b224-ea1eda6ce403/steps/e1ea21e9-834d-419d-bb38-12ab87e5b017/d8e466a0-a58a-4fcb-9633-9ee2e9ba95b5.png?crop=focalpoint&fit=crop&fp-x=0.8498&fp-y=0.0887&fp-z=2.9090&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=638&mark-y=196&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz03NSZoPTEyOCZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

</div>

#### Delete the ^^duplicate^^ dataset

<div class="grid" markdown>

Right click on the ^^duplicate^^ dataset.

![Step 9 screenshot](https://images.tango.us/workflows/d4e6501a-c2cf-4145-b224-ea1eda6ce403/steps/12336392-cc66-4bef-a25d-281bc67c1bef/ab3a415b-17ea-4829-a1db-9dae468cd63d.png?crop=focalpoint&fit=crop&fp-x=0.4623&fp-y=0.5036&fp-z=2.5546&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=460&mark-y=463&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz0yODAmaD04MiZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

Select Delete record.

![Step 10 screenshot](https://images.tango.us/workflows/d4e6501a-c2cf-4145-b224-ea1eda6ce403/steps/2c38d208-ddd3-40cf-b6d5-9bf897b4e4f9/ee6a2063-0a93-4eb6-92fc-94155db0fdd7.png?crop=focalpoint&fit=crop&fp-x=0.5794&fp-y=0.7589&fp-z=2.2245&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=400&mark-y=466&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz0zOTkmaD03NSZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

Click on Delete record in the confirmation dialog.

![Step 11 screenshot](https://images.tango.us/workflows/d4e6501a-c2cf-4145-b224-ea1eda6ce403/steps/97e9c3d6-69e0-4df7-9ca7-185ae225e775/caf96290-65bb-4189-a6e4-a62a4b0f559e.png?crop=focalpoint&fit=crop&fp-x=0.6081&fp-y=0.5569&fp-z=2.6308&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=474&mark-y=459&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz0yNTMmaD04OSZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

</div>

### [Asana](https://app.asana.com/1/653672074038961/home) Steps

#### Delete the ^^duplicate^^ dataset task

<div class="grid" markdown>

Right click on the ^^duplicate^^ dataset task.

![Step 12 screenshot](https://images.tango.us/workflows/d4e6501a-c2cf-4145-b224-ea1eda6ce403/steps/3d895e44-6645-43eb-9ff4-a645a83ff18c/62b7b90c-2b0f-4091-86a2-a091081de4e6.png?crop=focalpoint&fit=crop&fp-x=0.3471&fp-y=0.5286&fp-z=1.4753&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=266&mark-y=477&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz02NjkmaD01MyZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

Click on Delete task

![Step 13 screenshot](https://images.tango.us/workflows/d4e6501a-c2cf-4145-b224-ea1eda6ce403/steps/f99d8394-0567-49c0-b9c7-2b73370d523b/0c6b0416-c154-4ec7-8ec1-7f7f4b6f1e30.png?crop=focalpoint&fit=crop&fp-x=0.2423&fp-y=0.7733&fp-z=2.3502&w=1200&border=2%2CF4F2F7&border-radius=8%2C8%2C8%2C8&border-radius-inner=8%2C8%2C8%2C8&blend-align=bottom&blend-mode=normal&blend-x=0&blend-w=1200&mark-x=423&mark-y=462&m64=aHR0cHM6Ly9pbWFnZXMudGFuZ28udXMvc3RhdGljL2JsYW5rLnBuZz9tYXNrPWNvcm5lcnMmYm9yZGVyPTQlMkNGRjc0NDImdz0zNTQmaD04MyZmaXQ9Y3JvcCZjb3JuZXItcmFkaXVzPTEw)

</div>
