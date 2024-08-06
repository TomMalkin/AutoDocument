# Outcomes

Outcomes are the final result of Workflow. It can be a Word Document, a PDF, or an HTML document, for example. They are defined by a template which has fields that will be populated by AutoDocument, for example `{{name}}`. The data loaded by the Sources will have a value attributed to "name", which will be inserted into that field in the document. See [Templating](url_for('top.templating')) for more info.

Defining an Outcome involves defining the template, and defining the Output. A "File Storage" selection needs to be set for both. See [File Storages](url_for('top.file_storages')) for more info.

The Template File will be the base file that is used each time this Outcome is run.

The Output File will be where the final rendered file is saved to. This File Storage is special because the values of the Workflow can be used to render custom file paths. For example:

`/documents/'{{ client_id }}' Invoice.docx`

Indeed, using an Output File with a value in it like this is required when using Multi Record Sources, since otherwise the same file will be saved and overwritten each time the Outcome is calculated for each record!

You can specify as many Outcomes per Workflow as you like.
