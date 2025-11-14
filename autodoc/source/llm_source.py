"""Define the LLMSource Sources."""

from typing import Optional

from jinja2 import Template, TemplateSyntaxError
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from autodoc.data.tables import Source

from .source import SourceService


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
        rendered_prompt_text = prompt_template.render(**current_data or {})

        model = init_chat_model(
            self.source.llm.ModelName,
            model_provider=self.source.llm.provider.LangChainName,
            api_key=self.source.llm.APIKey,
            base_url=self.source.llm.BaseURL,
        )

        system_message = SystemMessage(
            content=self.source.LLMSystemPrompt or self.source.llm.SystemPrompt
        )

        human_message = HumanMessage(content=rendered_prompt_text)
        messages = [system_message, human_message]

        logger.info(
            f"Calling LLM with System Message {system_message} and Human Message {human_message}"
        )

        response = model.invoke(messages).content

        self.data[self.source.FieldName] = response

    def check(self) -> tuple[bool, Optional[str]]:
        """Check if this source can be loaded. Returns (can be loaded, reason why not)."""
        llm = self.source.llm
        if not llm:
            return False, "No LLM configuration found."
        if not llm.ModelName:
            return False, "No model name provided."
        if not llm.provider or not llm.provider.LangChainName:
            return False, "No provider defined."
        if not llm.APIKey:
            return False, "No API key provided."

        try:
            Template(self.source.LLMPromptTemplate)
        except TemplateSyntaxError as e:
            return False, f"Invalid Jinja2 template: {e}"

        try:
            _ = init_chat_model(
                llm.ModelName,
                model_provider=llm.provider.LangChainName,
                api_key=llm.APIKey,
                base_url=llm.BaseURL,
            )
        except Exception as e:
            return False, f"Failed to initialize model: {e}"

        return True, None
