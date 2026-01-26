from datetime import datetime, timezone
from pydantic import BaseModel, Field
from backend.services.aws.dynamo_database import DbManager
from dataclasses import dataclass
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional
from backend.services.data.enum import DbKeys
from boto3.dynamodb.conditions import Key
from enum import Enum
from backend.config.enum import TeamEnum


class PriorityLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class StatusLevel(str, Enum):
    NEW = "New"
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    DONE = "Done"


class PlannedTaskOutput(BaseModel):
    task_id: UUID = Field(..., description="Unique identifier for the task")
    feature: str = Field(..., description="Feature name associated with the task")
    description: str = Field(..., description="Detailed description of the task")
    dependencies: List[UUID] = Field(
        default_factory=list, description="List of task IDs that are dependencies"
    )
    status: StatusLevel = Field(..., description="Current status of the task")
    priority: PriorityLevel = Field(
        None, description="Priority level of the task (e.g., High, Medium, Low)"
    )
    assigned_to: Optional[TeamEnum] = Field(
        None, description="The team task has been assigned"
    )
    review_comments: Optional[str] = Field(
        None, description="Optional review comments for the task"
    )


class PlannedTaskOutputResponse(BaseModel):
    tasks: List[PlannedTaskOutput] = Field(..., description="List of planned tasks")


@dataclass
class Task:
    task_id: UUID
    feature: str
    description: str
    dependencies: List[UUID]
    status: StatusLevel
    priority: PriorityLevel
    created_at: datetime
    assigned_to: Optional[TeamEnum] = None
    review_comments: Optional[str] = None

    def to_json(self) -> dict:
        return {
            "task_id": str(self.task_id),
            "feature": self.feature,
            "description": self.description,
            "dependencies": [str(dep) for dep in self.dependencies],
            "status": self.status.value,
            "assigned_to": self.assigned_to.value if self.assigned_to else None,
            "priority": self.priority.value if self.priority else None,
            "review_comments": self.review_comments,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_parsed_response(cls, data: PlannedTaskOutput):
        return cls(
            task_id=data.task_id,
            feature=data.feature,
            description=data.description,
            dependencies=data.dependencies,
            status=data.status,
            assigned_to=TeamEnum(data.assigned_to) if data.assigned_to else None,
            priority=PriorityLevel(data.priority) if data.priority else None,
            review_comments=data.review_comments,
            created_at=datetime.now(timezone.utc),
        )

    @classmethod
    def to_cls(cls, data: dict):
        return cls(
            task_id=data["task_id"],
            feature=data["feature"],
            description=data["description"],
            dependencies=data["dependencies"],
            status=StatusLevel(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            assigned_to=TeamEnum(data.get("assigned_to")),
            priority=(
                PriorityLevel(data.get("priority")) if data.get("priority") else None
            ),
            review_comments=data.get("review_comments", None),
        )


class TaskDB:
    table = "CA#TASK"

    def __init__(self) -> None:
        self.db_manager = DbManager()

    def save_tasks(self, tasks: PlannedTaskOutputResponse) -> None:
        for task in tasks.tasks:
            try:
                self.db_manager.add_item(
                    {
                        DbKeys.Primary.value: self.table,
                        DbKeys.Secondary.value: str(task.task_id),
                        **Task.from_parsed_response(task).to_json(),
                    }
                )
            except Exception as e:
                pass

    def get_tasks(self) -> Optional[PlannedTaskOutputResponse]:
        results = self.db_manager.query_items(Key(DbKeys.Primary.value).eq(self.table))
        return [Task.to_cls(item) for item in results] if results else None

    def get_task_by_id(self, task_id: UUID) -> Optional[Task]:
        result = self.db_manager.get_item(
            {
                DbKeys.Primary.value: self.table,
                DbKeys.Secondary.value: str(task_id),
            }
        )
        if result:
            return Task.to_cls(result)
        return None

    def update_task(self, task: Task) -> None:
        try:
            self.db_manager.update_item(
                Key={
                    DbKeys.Primary.value: self.table,
                    DbKeys.Secondary.value: str(task.task_id),
                },
                UpdateExpression="""
                    SET feature = :feature,
                        description = :description,
                        dependencies = :dependencies,
                        status = :status,
                        assigned_to = :assigned_to,
                        priority = :priority,
                        review_comments = :review_comments
                """,
                ExpressionAttributeValues={
                    ":feature": task.feature,
                    ":description": task.description,
                    ":dependencies": [str(dep) for dep in task.dependencies],
                    ":status": task.status,
                    ":assigned_to": (
                        task.assigned_to.value if task.assigned_to else None
                    ),
                    ":priority": task.priority.value if task.priority else None,
                    ":review_comments": task.review_comments,
                },
            )
        except Exception as e:
            pass
