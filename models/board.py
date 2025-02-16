from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from fastapi import HTTPException, status
import base64
import json
from typing import Optional, Tuple

from core.database import Base
from schemas.board import BoardCreate, BoardUpdate

class Board(Base):
    __tablename__ = "boards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    public = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_count = Column(Integer, default=0)
    
    owner = relationship("User", back_populates="boards")
    posts = relationship("Post", back_populates="board")

    @classmethod
    async def create_board(cls, db: AsyncSession, board_data: BoardCreate, user_id: int) -> "Board":
        # 게시판 이름 중복 확인
        if await cls.get_board_by_name(db, board_data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Board name already exists"
            )
        
        # 새 게시판 생성
        db_board = cls(
            name=board_data.name,
            public=board_data.public,
            owner_id=user_id
        )
        db.add(db_board)
        await db.commit()
        await db.refresh(db_board)
        return db_board

    @classmethod
    async def get_board_by_id(cls, db: AsyncSession, board_id: int) -> Optional["Board"]:
        query = select(cls).where(cls.id == board_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_board_by_name(cls, db: AsyncSession, name: str) -> Optional["Board"]:
        query = select(cls).where(cls.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def update_board(cls, db: AsyncSession, board_id: int, board_data: BoardUpdate, user_id: int) -> "Board":
        board = await cls.get_board_by_id(db, board_id)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found"
            )
        
        # 소유자 확인
        if board.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this board"
            )
        
        # 이름이 변경되었고, 새 이름이 이미 존재하는 경우 확인
        if board_data.name != board.name and await cls.get_board_by_name(db, board_data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Board name already exists"
            )
        
        # 게시판 업데이트
        board.name = board_data.name
        board.public = board_data.public
        
        await db.commit()
        await db.refresh(board)
        return board

    @classmethod
    async def delete_board(cls, db: AsyncSession, board_id: int, user_id: int) -> None:
        board = await cls.get_board_by_id(db, board_id)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found"
            )
        
        if board.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this board"
            )
        
        await db.delete(board)
        await db.commit()

    @classmethod
    async def get_boards(
        cls, 
        db: AsyncSession, 
        user_id: int, 
        cursor: Optional[str] = None,
        limit: int = 10,
        sort_by_posts: bool = False
    ) -> Tuple[list["Board"], Optional[str]]:
        # 기본 쿼리
        query = select(cls).where(
            (cls.public == True) | (cls.owner_id == user_id)
        )
        
        # 커서 처리
        if cursor and cursor != "{{cursor}}":  # 템플릿 변수가 그대로 전달된 경우 무시
            try:
                cursor_data = json.loads(base64.b64decode(cursor))
                last_post_count = cursor_data['pc']
                last_id = cursor_data['id']
                
                if sort_by_posts:
                    query = query.where(
                        (cls.post_count < last_post_count) |
                        ((cls.post_count == last_post_count) & (cls.id < last_id))
                    )
                else:
                    query = query.where(cls.id < last_id)
            except:
                # 잘못된 커서 형식이면 첫 페이지처럼 처리
                pass
        
        # 정렬
        if sort_by_posts:
            query = query.order_by(desc(cls.post_count), desc(cls.id))
        else:
            query = query.order_by(desc(cls.id))
        
        # 결과 조회
        query = query.limit(limit + 1)
        result = await db.execute(query)
        boards = result.scalars().all()
        
        # 다음 페이지 존재 여부 확인
        has_next = len(boards) > limit
        if has_next:
            boards = boards[:-1]
        
        # 다음 커서 생성
        next_cursor = None
        if has_next and boards:
            last_board = boards[-1]
            cursor_data = {
                'pc': last_board.post_count,
                'id': last_board.id
            }
            next_cursor = base64.b64encode(
                json.dumps(cursor_data).encode()
            ).decode()
        
        return boards, next_cursor

    @classmethod
    async def get_accessible_board(cls, db: AsyncSession, board_id: int, user_id: int) -> Optional["Board"]:
        query = select(cls).where(
            cls.id == board_id,
            ((cls.public == True) | (cls.owner_id == user_id))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() 