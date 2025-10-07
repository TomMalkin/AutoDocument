{% raw %}

## Tutorial 1: The Basics of AutoDocument

Let's start by creating a simple workflow that asks a user for their name and age, then uses this information to generate a Word document.

First, create a new workflow on your AutoDocument Home Screen and name it "Tutorial 1".

### 1. Setting Up Your Form

Your form collects the information AutoDocument will use.
Click "Add Form Field" to add your first input:

*   **For the Name Field:**
    *   **Name:** `name` (This is the unique keyword AutoDocument uses for substitution.)
    *   **Label:** `Client's Name` (This is what the user sees on the form.)
    *   **Data Type:** `String` (Since a name is text.)
*   **For the Age Field:**
    *   **Name:** `age`
    *   **Label:** `Client's Age`
    *   **Data Type:** `Number`

### 2. Creating Your Document Outcome

Next, let's define what AutoDocument will produce.
If you have Microsoft Word, create a new `.docx` file with the following content:

```
Hi {{name}}, your age is {{age}}.
```

*(The double curly braces `{{ }}` tell AutoDocument to replace these with values from your form fields.)*

Now, back in AutoDocument, navigate to the "Outcomes" section and click "Add Microsoft Word":

*   **Template:** Select "Uploaded during Workflow" and give it the Unique Name: `Template`.
    *(This means you'll upload your Word document when you run the workflow.)*
*   **Output File:** Select "Downloaded after Workflow" and set the output name: `{{name}}.docx`.
    *(Yes, AutoDocument can use your field values to name the output file!)*

Click "Submit". Your workflow is now ready!

### 3. Running Your Workflow

1.  On the workflow page, click "Run".
2.  You'll see a form asking for the "Client's Name" and "Client's Age". Enter details like "Bob" and "25".
3.  You'll also be prompted to upload your Word document template.
4.  Click "Submit".

AutoDocument will display the live progress. Once complete, a "Download" button will appear. Click it to download a `.zip` file. Inside, you'll find a file named `Bob.docx`. Open it to confirm that "Bob" and "25" have replaced the placeholders in the document!

---

## Tutorial 2: Multi-Record Processing with CSV Files

AutoDocument excels at generating multiple documents from a single source of data, like a `.csv` file. In this tutorial, we'll create a workflow that uses a CSV to produce a separate Word document for each record.

Start by creating a new workflow and naming it "Tutorial 2".

### 1. Setting Up Your CSV Data Source

Click "Add a CSV Table". This type of source can either "Split" your workflow into separate runs for each record, or load all records into a single field.

*   Check the "Splitter" box.
    *(This tells AutoDocument to process each row in your CSV as a separate document.)*
*   **Source:** Select "Uploaded during Workflow" and give it the Unique Name: `Client Records`.
    *(You'll upload your CSV file when you run the workflow.)*
*   Click "Submit".

### 2. Prepare Your CSV File

Create a `.csv` file, for example `ClientRecords.csv`, with the following content:

````csv
name,age
John Doe,48
Jane Doe,35
Alice Bob,28
````

### 3. Creating Your Document Outcome

Now, let's define the output document, similar to Tutorial 1. Click "Add Microsoft Word" in the Outcomes section:

*   **Template:** Select "Uploaded during Workflow" with a Unique Name of `Template`.
    *(You can reuse the same Word document template from Tutorial 1, `Hi {{name}}, your age is {{age}}.`)*
*   **Output File:** Select "Downloaded after Workflow" and set the Output Name to `{{name}}.docx`.
*   Click "Submit".

### 4. Running Your Workflow

When you run this workflow, you'll upload your `ClientRecords.csv` file and your Word template. The downloaded `.zip` file will contain *three* Word documents—one for "John Doe", one for "Jane Doe", and one for "Alice Bob"—each personalized with the details from your CSV!

---

## Tutorial 3: Advanced Source Chaining (Example)

You can build powerful, complex workflows by combining multiple data sources. This tutorial illustrates an advanced example, assuming some initial setup of databases and file storage.

Imagine you manage clients in categories (A, B, C) and need to generate invoices for each client within a chosen category. Each invoice needs to list all ordered items, and then be saved to a client-specific folder on a shared network drive.

### Prerequisites (Assumed Setup)

*   **Database:** You have a database connected, perhaps named "Business Database" (see [Databases](databases.md) for setup).
*   **File Storage:** You have a Windows File Storage connected for network drives (see [File Storages](file_storages.md) for setup).

### The Workflow Steps

1.  **Client Category Form:**
    *   First, create a form field to ask the user for the client category.
    *   **Name:** `category`
    *   **Label:** `Client Category`
    *   **Data Type:** `String`

2.  **Retrieve Clients from Database (SQL RecordSet 1):**
    *   Add a "SQL RecordSet" source.
    *   Use a query like:
        ````sql
        SELECT client_id, client_name FROM Client WHERE category = :category
        ````
        *(The `:category` placeholder tells AutoDocument to use the value from the previous "category" form field.)*
    *   **Splitter:** Check this box.
        *(This will split the workflow for each client found, so each client gets their own invoice.)*
    *   Set this as **Step 1**.
    *   Now, each split workflow run will have `category`, `client_id`, and `client_name` available.

3.  **Retrieve Ordered Items from Database (SQL RecordSet 2):**
    *   Add another "SQL RecordSet" source.
    *   Use a query like:
        ````sql
        SELECT item_name, quantity FROM ItemOrder WHERE client_id = :client_id
        ````
        *(Each workflow split from the previous step will have a unique `client_id` for this query.)*
    *   **Field:** Check this box.
    *   **Field Name:** Set this to `items`.
        *(This will gather all items for the current client into a list named `items`, rather than splitting the workflow further.)*
    *   Set this as **Step 2** (it relies on `client_id` from Step 1).

### 4. Invoice Template Example

You can now design your Word template to loop through the `items` list:

````
Hi '{{ client_name }}',

Here is your invoice for your purchase of items:

{% for item in items %}
{{ item['quantity'] }} units of {{ item['item_name'] }}.
{% endfor %}
````

### 5. Saving Invoices to Network Drive (Microsoft Word Outcome)

Finally, configure your "Microsoft Word" outcome:

*   **Template:** Set the template path, e.g., `Templates\InvoiceTemplate.docx`.
    *(This assumes your template is stored in your configured Windows File Storage.)*
*   **Output File:** Set the output path using dynamic fields, e.g., `Invoices\{{client_id}}\Invoice.docx`.
    *(This will create a path like `\Invoices\123456\Invoice.docx` for client ID 123456.)*

You now have a robust workflow that can generate all invoices for a specific client category, dynamically pulling data from your database and saving them in organized folders on your network drive!
{% endraw %}
