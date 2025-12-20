"""Define constants."""

EXPLANATION_MAP = {
    "SQL Record": [
        "Add a Database Query that has 1 row of output.",
        "If more than one row is returned, then only the first is kept.",
        (
            "You can access data from previous Sources in the Workflow using "
            ":field syntax. For example, if 'client_id' was loaded in a "
            "previous step:"
        ),
        "SELECT Name, Age FROM Client WHERE ClientId = :client_id",
    ],
    "SQL RecordSet": [
        "Add a Database Query that can have multiple rows of output.",
        (
            "You can access data from previous Sources in the Workflow using "
            ":field syntax. For example, if 'client_id' was loaded in a "
            "previous step:"
        ),
        "SELECT Name, Age FROM Client WHERE ClientId = :client_id",
    ],
    "SQL RecordSet Transpose": [
        ("Add a Database Query where a 'Value' column is mapped to a 'Key' Column."),
        ("The Value column can then be referenced by the Key column in Outcome templates."),
    ],
    "CSVRecord": [
        "Add a single row of data from a .csv file.",
        "Each column can be accessed by its field name in the Outcome templates.",
        ("Horizontal Orientation refers to when the column names are the top row."),
    ],
    "CSVTable": [
        "Add multiple rows of data from a .csv file.",
        (
            "These rows can either split the Workflow (creating an output "
            "for each row) or be attached as a list to a single field for "
            "use in one template."
        ),
        (
            "In other words, if the .csv file has 3 rows, decide whether "
            "this should result in 3 output documents, or one output "
            "document containing the whole table."
        ),
    ],
    "ExcelRecord": [
        "Add a single row of data from an Excel file.",
        "Each column can be accessed by its field name in the Outcome templates.",
        (
            "Make sure to specify the sheet name and the row number where "
            "the column headers are located (usually Row 1)."
        ),
    ],
    "ExcelTable": [
        "Add multiple records from an Excel file.",
        "Each column can be accessed by its field name in the Outcome templates.",
        (
            "Make sure to specify the sheet name and the row number where "
            "the column headers are located (usually Row 1)."
        ),
        (
            "These rows can either split the Workflow (creating an output "
            "for each row) or be attached as a list to a single field for "
            "use in one template."
        ),
    ],
    "LLM": [
        "Get a response from a Large Language Model (LLM) and add it to the workflow context.",
        ("Choose a pre-configured LLM and build a prompt template using data from previous steps."),
        "The response from the LLM will be saved to the Field Name you specify.",
        (
            "NOTE: An administrator must configure an LLM in the 'Advanced "
            "-> Manage LLMs' section before this source can be used."
        ),
    ],
}
