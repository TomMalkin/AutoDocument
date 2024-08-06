# Overview

Welcome to AutoDocument.

Autodocument links various types of data sources - like Forms, Excel documents and SQL Queries, and outputs Documents like Microsoft Word, PDF or even text files. Create Workflows and link them to your users.

## Features

- **Powerful Templating**
  More than just inserting values into fields, leverage tools like if and while statements to delete or loop through blocks of text.

- **Data Splitting**
  Use Data Sources with multiple records to split the workflow, like generating a PDF for each line in a spreadsheet.

- **Customised Forms**
  Add HTML forms to kick off a Workflow

- **Data Source Chaining**
  Data Sources are loaded in order, so the information from one can be used in the next. See [Sources](url_for('top.sources')) for more info

- **Saving File Options**
  Download or upload on the fly, or read and write to network filesystems, S3 or Sharepoint Libraries

---

## Contents

[Sources](/sources.md)
[Outcomes](/outcomes.md)
[File Storages](file_storages.md)
[Databases](databases.md)
[Templating](templating.md)

# Installation

AutoDocument is designed to be used in a container. Run with:

`docker run autodocument -p 4605:4605`

AutoDocument works well with shared drives that are mounted in the container. If your shared drive is mounted on the host at `/mnt/shared_filesystem` then you can mount that to the AutoDocument container:

`docker run autodocument -p 4605:4605 -v /mnt/shared_filesystem:/shared_filesystem`

See [File Storages](/file_storages.md) for more info.

You may also want to change the admin password, which is loaded from ADMIN_PASSWORD, and defaulted to "admin":

`docker run autodocument -p 4605:4605 -e ADMIN_PASSWORD="MyPassword"`

---

# Quickstart

Once you've got a fresh installation of AutoDocument ready to go:

## Tutorial 1: The Basics

We're going to ask the user for Name and Age and then populate a Word Document.

AutoDocument uses repeatable Workflows. On the Home Screen create one called "Tutorial 1".

**Creating The Form**

Add the Name Field: Click on "Add Form Field"
the Name of the field is the keyword that will be substituted later. Type "name"
The Label of the field is what the user will see on the Form. Type "Client's Name"
This is some text - so select "String" as the Data Type

Add the Age Field: Click on "Add Form Field"
the Name of the field is the keyword that will be substituted later. Type "age"
The Label of the field is what the user will see on the Form. Type "Client's Age"
Select "Number" as the Data Type

**Creating The Outcome**

If you have access to a Microsoft Word Document, then create a .docx file somewhere.

`Hi {{name}}, your age is {{age}}.`

(The double "Curly Braces", { and }, tell AutoDocument that it is a field. ")

In AutoDocument, click "Add Microsoft Word" in the Outcomes Section.

We need to select where the template is coming from and how the output will be saved. Because we haven't linked any File Storages yet, we will upload the template and download the output.

Under Template, select "Uploaded during Workflow" with the Unique Name: "Template".

Under Output File, select Downloaded after Workflow with the output name: "{{ '{{name}}' }}.docx" (Yes, field substitutions work in file names!)

Submit

Our Workflow is ready to go!

**Running the Workflow**

Click Run on the workflow page. We are asked for the Client's Name and Age. Fill in some details like "Bob" aged 25. We also need to upload our Word Document from before. Hit Submit.

All going well, you should have downloaded a "output.zip" file, which when extracted has a **Bob.docx** (or **Bob.txt**) file in it. Open it to see the fields have been replaced with the values supplied on the form!

---

## Tutorial 2: Multi Record Sources

AutoDocument shines with Workflows that "Split" with Multi Record Sources, like a .csv with many records. We will create a workflow with a CSV file with 3 records in it, and generate a Word Document for each record.

Create a new Workflow called Tutorial 2

Click: Add a CSV Table. A MultiRecord Source like a CSV Table can either be used as a "Splitter", where the Workflow will spawn multiple child Workflows that will calculate their Outcomes separately, or as a "Field", where the multiple records are attached to a field name, and can be looped over in a template.

Check "Splitter".

We will upload the csv when we run the Workflow, similar to Tutorial 1. Choose "Uploaded during Workflow" and set the Unique Name as "Client Records". Submit.

Somewhere, create a .csv file with some records that can populate the same Word Document as Tutorial 1. For example:

`ClientRecords.csv:`

| name       | age |
|------------|-----|
| John Doe   | 48  |
| Jane Doe   | 35  |
| Alice Bob  | 28  |

Now we can add the Microsoft Word Outcome again. Click "Add Microsoft Word". Choose "Uploaded during Workflow" with a Unique Name of "Template", and Output File of "Downloaded after Workflow" with an Output Name of "{{name}}.docx"

When we run the Workflow now, we will download an output.zip file with 3 Word documents - one for each record.

## Tutorial 3: Source Chaining - Example

You can construct advanced Workflows by chaining sources together. This tutorial is more difficult to follow along because it assumes some infrastructure setup. But it demonstrates as an example the kinds of thing you can do with AutoDocument.

Lets say you had 3 classes of clients: A, B and C. And you wanted to generate invoices for each client within a category from a database. Each Invoice has a list of items that have been ordered, which we want listed in the invoice. We want to save each invoice in the client's folder on a shared Windows Drive called N:

**Setup**

We will assume we have a Database connected, called "Business Database" (see [Databases](url_for('top.databases')) for more info).

We also assume we have a Windows File Storage set up (see [File Storages](url_for('top.file_storages')) for more info)

Step 1 after creating the Workflow is to ask the user what category of Client. So we'll add a form with a name of "category", a label of "Client Category" and datatype of String.

Next we'll get a list of clients from our database using the answer to the "Category" question in the form.

If we add a SQL RecordSet, we can use an example query like:

`SELECT client_id, client_name from Client where category = :category`

The :category in the query tells AutoDocument to insert the value for "category" from any previous Source into the query. (It is also safe from SQL injection). We'll set it as a splitter, and leave it as Step 1.

This Workflow now splits for each record in this recordset, and will have the value "category", and one set of client_id and client_name in each Workflow.

We can use those values for the next step: another recordset. This time the query could be something like:

`SELECT item_name, quantity from ItemOrder where client_id = :client_id`

(Yes we could have used an inner join to just use one query but lets assume we can't.)

Note, each Workflow split from the original will have a different client_id, which has been sourced from the first query.

This time we aren't splitting the Workflow, because we want all the item details to be shown on the one invoice. Instead, we'll set the Field Name to be "items" and keep splitter unchecked. Now the results of this query will be saved as a list inside "items".

Make sure we set this query to Step 2, because it relies on data from a source within Step 1 (client_id).

We can loop through those items in a template like this:

```
Hi '{{ client_name }}',

Here is your invoice for your purchase of items:

{% for item in items %}
{{ item['quantity'] }} units of {{ item['item_name'] }}.
{% endfor %}
```

Now when we add our Microsoft Word document outcome lets use the Windows Share we setup previously. We'll set the template to be something like "Templates\InvoiceTemplate.docx"

The Output File can use the client_id to build the path, something like "Invoices\{{client_id}}\Invoice.docx", which would render to something like "\Invoices\123456\Invoice.docx"

We now have a repeatable Workflow that can generate all the Invoices for each client category.

