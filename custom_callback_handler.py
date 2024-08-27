from typing import Any
from langchain_community.callbacks import StreamlitCallbackHandler
from streamlit.external.langchain.streamlit_callback_handler import (
    StreamlitCallbackHandler,
    LLMThought,
)
from langchain.schema import AgentAction


class CustomStreamlitCallbackHandler(StreamlitCallbackHandler):
    def write_agent_name(self, name: str):
        self._parent_container.write(name)
