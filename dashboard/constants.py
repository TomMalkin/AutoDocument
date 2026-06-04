"""Define constants."""

EXPLANATION_MAP = {
    "Database": [
        "Add a Database Query that can have multiple rows of output.",
        (
            "You can access data from previous Sources in the Workflow using "
            ":field syntax. For example, if 'client_id' was loaded in a "
            "previous step:"
        ),
        "SELECT Name, Age FROM Client WHERE ClientId = :client_id",
    ],
    "CSV": [
        "Add one or more rows of data from a .csv file.",
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
    "Excel": [
        "Add one ore more records from an Excel file.",
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
