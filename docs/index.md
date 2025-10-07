{% raw %}

# Overview

Welcome to AutoDocument.

Autodocument links various types of data sources - like Forms, Spreadsheets and SQL Queries, and outputs Documents like Microsoft Word, PDF and text files. Create Workflows and link them to your users.

## Features

- **Powerful Templating**
  More than just inserting values into fields, leverage tools like if and while statements to delete or loop through blocks of text.

- **Data Splitting**
  Use Data Sources with multiple records to create multiple documents, like generating a PDF for each line in a spreadsheet.

- **Customised Forms**
  Add HTML forms to kick off a Workflow.

- **Data Source Chaining**
  Data Sources are loaded in order, so the information from one can be used in the next. Ask your user for a Client Id and then use that Id in the next SQL Statement. See [Sources](/sources.md) for more info.

- **Saving File Options**
  Download or upload on the fly, or read and write to network filesystems, S3 or Sharepoint Libraries.

- **Add an LLM Response**
  Write an LLM response directory to a document, and template prompts in the same way!

---

# How It Works

AutoDocument works by building a "dictionary" of keys to values as each source is loaded. One source might set "Name" to "Darryl Kerrigan", and the next might set something else. This dictionary is then used to populate the outcomes (documents like Word or PDFs) by referencing the keys of the dictionary, such as "Name".

---

## Contents

- [Tutorials](tutorials.md)
- [Sources](/sources.md)
- [Outcomes](/outcomes.md)
- [File Storages](file_storages.md)
- [Databases](databases.md)
- [Templating](templating.md)
- [Deployment](deployment.md)
- [LLMs](llm.md)

# Installation

AutoDocument is designed to be used in containers. Run a basic setup using this docker-compose template. More options at [Deployment](/deployment.md). 

```yaml
services:
  redis:
    image: "docker.io/redis:7-alpine"

  app:
    image: tommalkin/autodocument:latest
    ports:
      - "4605:4605"
    volumes:
      - download_dir:/download_dir
      - upload_dir:/upload_dir
      - db_data:/db_data
    depends_on:
      - redis

  worker:
    image: tommalkin/autodocument-worker:latest
    volumes:
      - download_dir:/download_dir
      - upload_dir:/upload_dir
      - db_data:/db_data
    depends_on:
      - redis
    command: ["dramatiq", "autodoc.tasks", "--processes", "1"]

volumes:
  download_dir: {}
  upload_dir: {}
  db_data: {}
```

After deploying, visit the web app on port 4605, and check out some [Quickstart Tutorials](tutorials.md)!

{% endraw %}
