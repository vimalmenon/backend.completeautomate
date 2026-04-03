import humps
from pydantic import BaseModel, ConfigDict


class BaseModelWithConfig(BaseModel):
    model_config = ConfigDict(
        alias_generator=humps.camelize,
        populate_by_name=True,
        serialize_by_alias=True,
        use_enum_values=True,
    )
