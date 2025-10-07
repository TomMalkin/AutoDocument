# LLMs

AutoDocument can send a prompt to an LLM and use the response in the document generation.

The prompt can be templated just like any outcome, leading to highly dynamic workflows.

# Managing LLMs

The administrator must add an LLM in the Manage LLM admin page.

1) Select Provider from the list
2) Provide a model name from that provider
3) Base URL (Optional): If you are running for example an Ollama instance, use this to set the url of it.
4) API Key: Of whatever provider you are using
5) System Prompt Default: This can be overriden on a per Source level.


# In a Workflow

Click on LLM Response under Add Sources.

Select an LLM from the list.

Write the prompt template. For example, if you load a value to the field "topic" from another source in a previous step:

```text
Write a poem about {{ topic }}
```

Optional: Override the system prompt.

Field Name: The LLM response will be saved to this field just like other sources.




