{% raw %}
# Outcomes

Outcomes are the final result of Workflow. It can be a Word Document, a PDF, or an Text document for example. They are defined by a template which contain text fields that will be populated by AutoDocument, for example `{{name}}`. The data loaded by the sources will have a value attributed to "name", which will be inserted into that field in the document. See [Templating](/tempating.md) for more info.

Defining an Outcome involves defining the template, and defining the output location. A "File Storage" selection needs to be set for both. See [File Storages](/file_storages.md) for more info. A File Storage selection can be a location to save the generated files, or simply zipped and downloaded straight from the web app.

The template file will be the base file that is used each time this Outcome is run.

The output file will be where the final rendered file is saved to. The output file can have the values of the Workflow used to render custom file paths. For example:

`/documents/'{{ client_id }}' Invoice.docx`

(Indeed, using an Output File with a value in it like this is required when using Multi Record Sources, since otherwise the same file will be saved and overwritten each time the Outcome is calculated for each record!)

You can specify as many Outcomes per Workflow as you like.

{% endraw %}
