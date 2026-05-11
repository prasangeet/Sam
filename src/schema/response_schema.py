from typing import Optional, Dict, Any
from pydantic import BaseModel


class ProfileSchema(BaseModel):
    name: Optional[str] = None
    date_of_birth: Optional[str] = None


class MemorySchema(BaseModel):
    fact: Optional[str] = None


class ActionSchema(BaseModel):
    type: str = "none"
    params: Dict[str, Any] = {}


class ResponseContentSchema(BaseModel):
    content: str = "Sorry, I didn't understand that."


class ResponseSchema(BaseModel):
    profile: ProfileSchema = ProfileSchema()
    memory: MemorySchema = MemorySchema()
    action: ActionSchema = ActionSchema()
    response: ResponseContentSchema = ResponseContentSchema()
