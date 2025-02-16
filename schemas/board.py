from pydantic import BaseModel, Field
from typing import List, Optional

class BoardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    public: bool = True

class BoardUpdate(BoardCreate):
    pass

class BoardResponse(BoardCreate):
    id: int
    owner_id: int
    post_count: int = 0
    
    class Config:
        from_attributes = True

class BoardList(BaseModel):
    items: List[BoardResponse]
    next_cursor: Optional[str] = None 