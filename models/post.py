from sqlalchemy import Column, Integer, String, Text, ForeignKey, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from fastapi import HTTPException, status
from typing import Optional, Tuple, List
import base64

from core.database import Base
from schemas.post import PostCreate, PostUpdate
from models.board import Board

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    
    author = relationship("User", back_populates="posts")
    board = relationship("Board", back_populates="posts")

    @classmethod
    async def create_post(cls, db: AsyncSession, post_data: PostCreate, user_id: int, board: Board) -> "Post":
        db_post = cls(
            title=post_data.title,
            content=post_data.content,
            author_id=user_id,
            board_id=board.id
        )
        
        # 게시판의 게시글 수 증가
        board.post_count += 1
        
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)
        return db_post

    @classmethod
    async def get_post_by_id(cls, db: AsyncSession, post_id: int) -> Optional["Post"]:
        query = select(cls).where(cls.id == post_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def update_post(cls, db: AsyncSession, post_id: int, post_data: PostUpdate, user_id: int) -> "Post":
        post = await cls.get_post_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        if post.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this post"
            )
        
        post.title = post_data.title
        post.content = post_data.content
        
        await db.commit()
        await db.refresh(post)
        return post

    @classmethod
    async def delete_post(cls, db: AsyncSession, post_id: int, user_id: int) -> None:
        post = await cls.get_post_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        if post.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this post"
            )
        
        # 게시판의 게시글 수 감소
        board = await Board.get_board_by_id(db, post.board_id)
        if board:
            board.post_count -= 1
        
        await db.delete(post)
        await db.commit()

    @classmethod
    async def get_posts_by_board(
        cls,
        db: AsyncSession,
        board_id: int,
        cursor: Optional[str] = None,
        limit: int = 10
    ) -> Tuple[List["Post"], Optional[str]]:
        # 기본 쿼리
        query = select(cls).where(cls.board_id == board_id)
        
        # 커서 처리
        if cursor and cursor != "{{cursor}}":
            try:
                last_id = int(base64.b64decode(cursor))
                query = query.where(cls.id < last_id)
            except:
                pass
        
        # 정렬 및 제한
        query = query.order_by(desc(cls.id)).limit(limit + 1)
        
        # 결과 조회
        result = await db.execute(query)
        posts = result.scalars().all()
        
        # 다음 페이지 존재 여부 확인
        has_next = len(posts) > limit
        if has_next:
            posts = posts[:-1]
        
        # 다음 커서 생성
        next_cursor = None
        if has_next and posts:
            last_post = posts[-1]
            next_cursor = base64.b64encode(str(last_post.id).encode()).decode()
        
        return posts, next_cursor 