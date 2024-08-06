# Sources

Sources are the inputs to a Workflow: Databases, Spreadsheets and Custom HTML forms for example. They can be chained together in order to use the data from one source in the next. Sources are either a form field, where the user is presented with a form at the start of the Workflow, a Single Record Source where the source is just a set of keys to values, or a Multi Record Source like a SQL query output or a spreadsheet with multiple rows.

## Steps

When adding any Source, you choose the Step value to set the order of when the Source is loaded. If Source B requires some data from Source A, make sure Source B has a higher Step value than Source A.

---

## Single Record Source

A Single Record Source is a the most simple Source. An example is a .csv file with a single line of data, e.g.:

```
| Id | name            | age | address                        |
|----|-----------------|-----|--------------------------------|
| 1  | Darryl Kerrigan | 48  | 3 Highview Crescent, Coolaroo |
```

If this Source was added to a Workflow, then you could use the fields `{{name}}, {{age}}` etc in the Outcome Templates.

---

## Multi Record Source

Multi Record Sources are Sources where multiple sets of data are set to the same field names, for example a .csv with multiple lines:

```
| Id | name           | age | address                   |
|----|----------------|-----|---------------------------|
| 1  | Darryl Kerrigan| 48  | 3 Highview Crescent, Coolaroo |
| 2  | Cliff Buxton   | 52  | Parkes Radio Telescope    |
```

Multi Record Sources are added as either a Splitter or set to a Field.

### Splitter

Splitters will take any current data loaded by the other Sources, and generate new Workflows, one for each record in the Multi Record Source. For example with the above table, if you have a Form Field called "category" with a user submitted value of "A", then the first split workflow will have category = "A", name = "Darryl Kerrigan", etc, while the second will have category = "A", name = "Cliff Buxton" and so on.

Use splitters to generate multiple outcomes in a single workflow based on the same template.

### Field

When Field is selected, then the entire contents of the multi-record source is added to a single field, for example with the above table if we set the field name to be "characters" after adding the same category field, then the Workflow would have category = "A", characters = [(name="Darryl Kerrigan", ...), (name="Cliff Buxton", ...)] etc.

You can loop over these values in templates to create lists or tables within the one template. See [Templating](url_for('top.templating')) for more details.

---

## Chaining

Data loaded in a Source in a previous Step can be used in a later Source. For example, if you wanted to only create a document for a specific category of client in a database query, you could create a form field that asks for the category, and then use it in the subsequent query. For example the query could look like:

```sql
SELECT client_id, Name from Client where Category = :category
```

The `:category` marker in the query will be populated by the category selected in the previous source. Note: this is SQL Injection Safe.

---

## How it works

AutoDocument works by building a "Dictionary" of Keys to Values as each source is loaded. One source might set "Name" to "Darryl Kerrigan", and the next might set something else. This dictionary is then used to populate the Outcome Documents by referencing the keys of the dictionary, such as "Name".

