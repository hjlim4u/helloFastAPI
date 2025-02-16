from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional, Tuple, List

from models.post import Post
from models.board import Board
from schemas.post import PostCreate, PostUpdate, PostResponse

class PostService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_post(self, post_data: PostCreate, user_id: int) -> PostResponse:
        try:
            board = await Board.get_accessible_board(self.db, post_data.board_id, user_id)
            if not board:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Board not found or not accessible"
                )
            
            post = await Post.create_post(self.db, post_data, user_id, board)
            return PostResponse.model_validate(post)
        except Exception as e:
            raise
    
    async def update_post(self, post_id: int, post_data: PostUpdate, user_id: int) -> PostResponse:
        post = await Post.update_post(self.db, post_id, post_data, user_id)
        return PostResponse.model_validate(post)
    
    async def delete_post(self, post_id: int, user_id: int) -> None:
        await Post.delete_post(self.db, post_id, user_id)
    
    async def get_post(self, post_id: int, user_id: int) -> PostResponse:
        post = await Post.get_post_by_id(self.db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # 게시판 접근 권한 확인
        board = await Board.get_accessible_board(self.db, post.board_id, user_id)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this post"
            )
            
        return PostResponse.model_validate(post)
    
    async def get_posts(
        self,
        board_id: int,
        user_id: int,
        cursor: Optional[str] = None,
        limit: int = 10
    ) -> Tuple[List[PostResponse], Optional[str]]:
        # 게시판 접근 권한 확인
        board = await Board.get_accessible_board(self.db, board_id, user_id)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found or not accessible"
            )
        
        posts, next_cursor = await Post.get_posts_by_board(
            self.db,
            board_id,
            cursor,
            limit
        )
        return [PostResponse.model_validate(post) for post in posts], next_cursor 