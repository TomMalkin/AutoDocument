{% raw %}

# Overview

Welcome to AutoDocument.

Autodocument links various types of data sources - like Forms, Spreadsheets and SQL Queries, and outputs Documents like Microsoft Word, PDF or even text files. Create Workflows and link them to your users.

## Features

- **Powerful Templating**
  More than just inserting values into fields, leverage tools like if and while statements to delete or loop through blocks of text.

- **Data Splitting**
  Use Data Sources with multiple records to split the workflow, like generating a PDF for each line in a spreadsheet.

- **Customised Forms**
  Add HTML forms to kick off a Workflow.

- **Data Source Chaining**
  Data Sources are loaded in order, so the information from one can be used in the next. See [Sources](/sources.md) for more info.

- **Saving File Options**
  Download or upload on the fly, or read and write to network filesystems, S3 or Sharepoint Libraries.

---

# How It Works

AutoDocument works by building a "dictionary" of keys to values as each source is loaded. One source might set "Name" to "Darryl Kerrigan", and the next might set something else. This dictionary is then used to populate the outcomes (documents like Word or PDFs) by referencing the keys of the dictionary, such as "Name".

---

## Contents

- [Sources](/sources.md)
- [Outcomes](/outcomes.md)
- [File Storages](file_storages.md)
- [Databases](databases.md)
- [Templating](templating.md)
- [Tutorials](tutorials.md)

# Installation

AutoDocument is designed to be used in a container. Run with:

`docker run -p 4605:4605 docker.io/tommalkin/autodocument:latest`

AutoDocument works well with shared drives that are mounted in the container. If your shared drive is mounted on the host at `/mnt/shared_filesystem` then you can mount that to the AutoDocument container:

`docker run -p 4605:4605 -v /mnt/shared_filesystem:/shared_filesystem docker.io/tommalkin/autodocument:latest`

See [File Storages](/file_storages.md) for more info.

You may also want to change the admin password, which is loaded from ADMIN_PASSWORD, and defaulted to "admin":

`docker run -p 4605:4605 -e ADMIN_PASSWORD="MyPassword" docker.io/tommalkin/autodocument:latest`

Then checkout some [Quickstart Tutorials](tutorials.md)!

{% endraw %}
