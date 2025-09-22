"""Define the LLMSource Sources."""

from jinja2 import Template
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from autodoc.data.tables import Source

from .source import SourceService

from loguru import logger


class LLMSourceService(SourceService):
    """A Response from an LLM."""

    is_multi_record = False

    def __init__(self, source: Source, **kwargs) -> None:
        """Initialise the CSVRecordSourceService with the file_path of the file."""
        self.source = source
        self.data: dict = {}

    def load_data(self, current_data: dict | None = None) -> None:
        """Set the response to the llm key."""
        prompt_template_text = self.source.LLMPromptTemplate
        prompt_template = Template(prompt_template_text)
        rendered_prompt_text = prompt_template.render(**current_data)

        model = init_chat_model(
            self.source.llm.ModelName,
            model_provider=self.source.llm.provider.LangChainName,
            api_key=self.source.llm.APIKey,
            base_url=self.source.llm.BaseURL,
        )

        system_message = SystemMessage(content=self.source.LLMSystemPrompt or self.source.llm.SystemPrompt)

        human_message = HumanMessage(content=rendered_prompt_text)
        messages = [system_message, human_message]

        logger.info(f"Calling LLM with System Message {system_message} and Human Message {human_message}")

        response = model.invoke(messages).content

        self.data[self.source.FieldName] = response
