from pydantic import BaseModel, alias_generators, ConfigDict


class PtBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
    )
