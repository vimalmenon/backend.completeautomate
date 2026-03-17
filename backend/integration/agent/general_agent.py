import logging

from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel

from backend.config.env import env
from backend.data import MessageDBData
from backend.database import AgentMessageDB
from backend.exception.app_exception import AppException
from backend.services.agent_service import AgentImageService, AgentService

logger = logging.getLogger(__name__)


class GeneralAgent:

    def __init__(self, agent: AgentService | AgentImageService, response_format=None):
        if isinstance(agent, AgentService):
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
        if isinstance(agent, AgentImageService):
            self.agent = agent

    def invoke(self):
        if isinstance(self.agent, AgentService):
            logger.info("Invoking general agent for team=%s", self.team.name)
            messages = [
                SystemMessage(content=self.agent.get_system_message()),
                HumanMessage(content=self.agent.get_prompt()),
            ]
            if env.OFFLINE:
                result = self.__mock_offline_result(messages)
            else:
                agent = self.__create_agent()
                result = agent.invoke(
                    {
                        "messages": messages,
                        "user_preferences": {
                            "style": "technical",
                            "verbosity": "detailed",
                        },
                    }
                )
            data = MessageDBData(
                task_id=self.task_id,
                messages=self.parse_messages_to_dict(result["messages"]),
            )
            self.agent_db.save_message(data)
            logger.info(
                "General agent invocation completed for team=%s", self.team.name
            )
            return result
        raise AppException("Not a valid instance")

    def generate(self) -> bytes:
        if isinstance(self.agent, AgentImageService):
            image_model = self.agent.get_model()
            return image_model.generate(prompt=self.agent.prompt)
        raise AppException("Not a image valid instance")

    def reinvoke(self, message: str):
        db_data = self.agent_db.get_messages_by_task_id(self.task_id)
        if not db_data:
            raise AppException("data not found")
        messages = self.__convert_msg_dict_for_reinvoke(db_data.messages)
        messages.append(HumanMessage(content=message))
        if env.OFFLINE:
            result = self.__mock_offline_result(messages)
        else:
            agent = self.__create_agent()
            result = agent.invoke(
                {
                    "messages": messages,
                    "user_preferences": {
                        "style": "technical",
                        "verbosity": "detailed",
                    },
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

    def __mock_offline_result(self, messages: list) -> dict:
        logger.info("OFFLINE mode enabled: returning mock AI response")
        ai_message = AIMessage(
            content=(
                "[OFFLINE MOCK RESPONSE] This is a simulated AI response generated "
                "because OFFLINE mode is enabled."
            )
        )
        result = {
            "messages": [*messages, ai_message],
        }
        structured_response = self.__build_mock_structured_response()
        if structured_response is not None:
            result["structured_response"] = structured_response
        return result

    def __build_mock_structured_response(self):
        if not self.response_format:
            return None

        try:
            if self.response_format.__name__ == "YouTubeVideoAnalyzerListResponse":
                return self.response_format(
                    details=[
                        {
                            "title": "[OFFLINE] Mock Video Title",
                            "description": "[OFFLINE] Mock description generated for testing.",
                            "tags": ["offline", "mock", "youtube"],
                        }
                    ]
                )

            if self.response_format.__name__ == "ImagePromptsListRequest":
                return self.response_format(
                    image_prompts=[
                        {
                            "name": "offline_mock_thumbnail.png",
                            "prompt": "A clean YouTube thumbnail with bold headline typography and high contrast subject.",
                            "description": "[OFFLINE] Mock thumbnail prompt for local testing.",
                            "negative_prompt": "blurry, low resolution, watermark, distorted face",
                        }
                    ]
                )

            if issubclass(self.response_format, BaseModel):
                return self.response_format.model_construct()

        except Exception as exc:
            logger.warning("Failed to build mock structured response: %s", exc)

        return None
