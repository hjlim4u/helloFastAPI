from fastapi import APIRouter, Depends, status, Query
from typing import Optional

from core.database import get_db
from services.post import PostService
from schemas.post import PostCreate, PostUpdate, PostResponse, PostList
from routers.auth import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])

async def get_post_service(db = Depends(get_db)) -> PostService:
    return PostService(db)

@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    post_service: PostService = Depends(get_post_service),
    current_user_id: int = Depends(get_current_user)
) -> PostResponse:
    try:
        post = await post_service.create_post(post_data, current_user_id)
        return post
    except Exception as e:
        raise

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    post_service: PostService = Depends(get_post_service),
    current_user_id: int = Depends(get_current_user)
) -> PostResponse:
    try:
        post = await post_service.update_post(post_id, post_data, current_user_id)
        return post
    except Exception as e:
        raise

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    post_service: PostService = Depends(get_post_service),
    current_user_id: int = Depends(get_current_user)
):
    try:
        await post_service.delete_post(post_id, current_user_id)
    except Exception as e:
        raise

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    post_service: PostService = Depends(get_post_service),
    current_user_id: int = Depends(get_current_user)
) -> PostResponse:
    try:
        post = await post_service.get_post(post_id, current_user_id)
        return post
    except Exception as e:
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