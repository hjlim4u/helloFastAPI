from fastapi import APIRouter, Depends, status, Query
from typing import Optional
import logging

from core.database import get_db
from services.post import PostService
from schemas.post import PostCreate, PostUpdate, PostResponse, PostList
from routers.auth import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

async def get_post_service(db = Depends(get_db)) -> PostService:
    return PostService(db)

@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    post_service: PostService = Depends(get_post_service),
    current_user_id: int = Depends(get_current_user)
) -> PostResponse:
    logger.debug(f"Creating post with data: {post_data}")
    try:
        post = await post_service.create_post(post_data, current_user_id)
        logger.debug(f"Post created successfully: {post}")
        return post
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        raise

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    post_service: PostService = Depends(get_post_service),
    current_user_id: int = Depends(get_current_user)
) -> PostResponse:
    logger.debug(f"Updating post {post_id} with data: {post_data}")
    try:
        post = await post_service.update_post(post_id, post_data, current_user_id)
        logger.debug(f"Post updated successfully: {post}")
        return post
    except Exception as e:
        logger.error(f"Error updating post: {str(e)}")
        raise

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    post_service: PostService = Depends(get_post_service),
    current_user_id: int = Depends(get_current_user)
):
    logger.debug(f"Deleting post {post_id}")
    try:
        await post_service.delete_post(post_id, current_user_id)
        logger.debug(f"Post {post_id} deleted successfully")
    except Exception as e:
        logger.error(f"Error deleting post: {str(e)}")
        raise

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    post_service: PostService = Depends(get_post_service),
    current_user_id: int = Depends(get_current_user)
) -> PostResponse:
    logger.debug(f"Getting post {post_id}")
    try:
        post = await post_service.get_post(post_id, current_user_id)
        logger.debug(f"Post retrieved successfully: {post}")
        return post
    except Exception as e:
        logger.error(f"Error getting post: {str(e)}")
        raise

@router.get("/board/{board_id}", response_model=PostList)
async def get_posts(
    board_id: int,
    cursor: Optional[str] = None,
    limit: int = Query(default=10, le=100),
    post_service: PostService = Depends(get_post_service),
    current_user_id: int = Depends(get_current_user)
) -> PostList:
    posts, next_cursor = await post_service.get_posts(
        board_id,
        current_user_id,
        cursor,
        limit
    )
    return PostList(
        items=posts,
        next_cursor=next_cursor
    ) 