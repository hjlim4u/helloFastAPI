from pydantic import BaseModel, Field
from typing import List, Optional

class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)

class PostCreate(PostBase):
    board_id: int

class PostUpdate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    author_id: int
    board_id: int
    
    class Config:
        from_attributes = True

class PostList(BaseModel):
    items: List[PostResponse]
    next_cursor: Optional[str] = None 