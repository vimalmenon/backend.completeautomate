import logging

from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage, SystemMessage

from backend.data import MessageDBData
from backend.database import AgentMessageDB
from backend.exception.app_exception import AppException
from backend.services.agent_service import AgentService

logger = logging.getLogger(__name__)


class GeneralAgent:

    def __init__(self, agent: AgentService, response_format=None):
        self.agent = agent
        prompt_data = self.agent.prompt_data
        self.task_id = self.agent.task_id
        if not prompt_data:
            raise AppException("Prompt data is required for GeneralAgent")
        self.agent_db = AgentMessageDB()
        self.team = prompt_data.role
        self.prompt = agent.get_prompt()
        self.response_format = response_format
        logger.debug("GeneralAgent initialized for team=%s", self.team.name)

    def invoke(self):
        logger.info("Invoking general agent for team=%s", self.team.name)
        agent = self.__create_agent()
        messages = [
            SystemMessage(content=self.agent.get_system_message()),
            HumanMessage(content=self.agent.get_prompt()),
        ]
        result = agent.invoke(
            {
                "messages": messages,
                "user_preferences": {"style": "technical", "verbosity": "detailed"},
            }
        )
        data = MessageDBData(
            task_id=self.task_id,
            messages=self.parse_messages_to_dict(result["messages"]),
        )
        self.agent_db.save_message(data)
        logger.info("General agent invocation completed for team=%s", self.team.name)
        return result

    def reinvoke(self, message: str):
        db_data = self.agent_db.get_messages_by_task_id(self.task_id)
        if not db_data:
            raise AppException("data not found")
        messages = self.__convert_msg_dict_for_reinvoke(db_data.messages)
        messages.append(HumanMessage(content=message))
        agent = self.__create_agent()
        result = agent.invoke(
            {
                "messages": messages,
                "user_preferences": {"style": "technical", "verbosity": "detailed"},
            }
        )
        data = MessageDBData(
            task_id=self.task_id,
            messages=self.parse_messages_to_dict(result["messages"]),
        )
        self.agent_db.update_message(data)
        logger.info("General agent invocation completed for team=%s", self.team.name)
        return result

    def __create_agent(self):
        logger.debug("Creating LangChain agent for team=%s", self.team.name)
        return create_agent(
            name=self.team.name,
            model=self.agent.get_model(),
            response_format=self.response_format,
        )

    def parse_messages_to_dict(self, messages: list) -> list[dict]:
        return [
            {
                "content": message.content,
                "role": self.__check_role(message),
                "id": message.id,
            }
            for message in messages
        ]

    def __check_role(self, message):
        if isinstance(message, HumanMessage):
            return "human"
        elif isinstance(message, SystemMessage):
            return "system"
        elif isinstance(message, AIMessage):
            return "ai"
        else:
            return "unknown"

    def __convert_msg_dict_for_reinvoke(self, messages) -> list:
        return [self.__convert_to_message(message) for message in messages]

    def __convert_to_message(self, message: dict):
        if message["role"] == "system":
            return SystemMessage(content=message["content"])
        if message["role"] == "ai":
            return AIMessage(content=message["content"])
        if message["role"] == "human":
            return HumanMessage(content=message["content"])
        raise AppException("No Compatible role type")
