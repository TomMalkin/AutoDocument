{% raw %}
# Sources

Sources are the inputs to a Workflow: databases, spreadsheets and custom HTML forms for example. They can be chained together in order to use the data from one source in the next. Sources are either a form field, where the user is presented with a form at the start of the Workflow, a single record source where the source is just a set of keys to values, or a multi record source like a SQL query output or a spreadsheet with multiple rows.

## Steps

When adding any source, you choose the step value to set the order of when the source is loaded. If source B requires some data from source A, make sure source B has a higher step value than source A.

---

## Single Record Source

A single record source is a the most simple source. An example is a .csv file with a single line of data, e.g.:

```
| Id | name            | age | address                       |
|----|-----------------|-----|-------------------------------|
| 1  | Darryl Kerrigan | 48  | 3 Highview Crescent, Coolaroo |
```

If this source was added to a Workflow, you could then use the fields `{{name}}, {{age}}` etc in the outcome templates.

---

## Multi Record Source

Multi record sources are sources where multiple sets of data are set to the same field names, for example a .csv with multiple lines:

```
| Id | name            | age | address                       |
|----|-----------------|-----|-------------------------------|
| 1  | Darryl Kerrigan | 48  | 3 Highview Crescent, Coolaroo |
| 2  | Cliff Buxton    | 52  | Parkes Radio Telescope        |
```

Multi record sources are added as either a 'Splitter' or set to a 'Field'.

### Splitter

Splitters will take any current data loaded by the other sources, and generate new Workflows, one for each record in the multi record source. For example with the above table, if you have a form field called "category" with a user submitted value of "A", then the first split Workflow will have category = "A", name = "Darryl Kerrigan", etc, while the second will have category = "A", name = "Cliff Buxton" and so on.

Use splitters to generate multiple outcomes in a single Workflow based on the same template.

### Field

When 'Field' is selected, then the entire contents of the multi-record source is added to a single field, for example with the above table if we set the field name to be "characters" after adding the same category field, then the Workflow would have category = "A", characters = `[(name="Darryl Kerrigan", ...), (name="Cliff Buxton", ...)]` etc.

You can loop over these values in templates to create lists or tables within the one template. See [Templating](/templating.md) for more details.

---

## Chaining

Data loaded in a source in a previous step can be used in a later source. For example, if you wanted to only create a document for a specific category of client in a database query, you could create a form field that asks for the category, and then use it in the subsequent query. For example the query could look like:

```sql
SELECT client_id, Name from Client where Category = :category
```
The `:category` marker in the query will be populated by the category selected in the previous source. Note: this is SQL injection Safe.

{% endraw %}
