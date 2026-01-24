from pydantic import BaseModel, Field
from backend.services.aws.dynamo_database import DbManager
from dataclasses import dataclass
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional
from backend.services.data.enum import DbKeys
from boto3.dynamodb.conditions import Key


class PlannedTaskOutput(BaseModel):
    task_id: UUID = Field(..., description="Unique identifier for the task")
    feature: str = Field(..., description="Feature name associated with the task")
    description: str = Field(..., description="Detailed description of the task")
    dependencies: List[UUID] = Field(
        default_factory=list, description="List of task IDs that are dependencies"
    )
    status: str = Field(..., description="Current status of the task")
    assigned_to: Optional[str] = Field(
        None, description="Name of the person assigned to the task"
    )
    priority: Optional[str] = Field(
        None, description="Priority level of the task (e.g., High, Medium, Low)"
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
    status: str
    assigned_to: Optional[str] = None
    priority: Optional[str] = None
    review_comments: Optional[str] = None

    def to_json(self) -> dict:
        return {
            "task_id": str(self.task_id),
            "feature": self.feature,
            "description": self.description,
            "dependencies": [str(dep) for dep in self.dependencies],
            "status": self.status,
            "assigned_to": self.assigned_to,
            "priority": self.priority,
            "review_comments": self.review_comments,
        }

    @classmethod
    def from_parsed_response(cls, data: PlannedTaskOutput):
        return cls(
            task_id=data.task_id,
            feature=data.feature,
            description=data.description,
            dependencies=data.dependencies,
            status=data.status,
            assigned_to=data.assigned_to,
            priority=data.priority,
            review_comments=data.review_comments,
        )


class TaskDB:
    table = "CA#TASK"

    def __init__(self) -> None:
        self.db_manager = DbManager()

    def save_tasks(self, tasks: PlannedTaskOutputResponse) -> None:
        breakpoint()
        for task in tasks.tasks:
            breakpoint()
            try:
                self.db_manager.add_item(
                    {
                        DbKeys.Primary.value: self.table,
                        DbKeys.Secondary.value: str(task.task_id),
                        **Task.from_parsed_response(task).to_json(),
                    }
                )
            except Exception as e:
                breakpoint()
                pass

    def get_tasks(self) -> Optional[PlannedTaskOutputResponse]:
        return self.db_manager.query_items(
            Key(DbKeys.Primary.value).eq(self.table)
        )
