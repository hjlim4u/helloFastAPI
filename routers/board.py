from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from services.board import BoardService
from services.user import UserService
from schemas.board import BoardCreate, BoardUpdate, BoardResponse, BoardList
from routers.auth import oauth2_scheme, get_user_service, get_current_user

router = APIRouter(prefix="/boards", tags=["boards"])

async def get_board_service(db = Depends(get_db)) -> BoardService:
    return BoardService(db)

@router.post("", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
async def create_board(
    board_data: BoardCreate,
    board_service: BoardService = Depends(get_board_service),
    current_user_id: int = Depends(get_current_user)
) -> BoardResponse:
    return await board_service.create_board(board_data, current_user_id)

@router.put("/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: int,
    board_data: BoardUpdate,
    board_service: BoardService = Depends(get_board_service),
    current_user_id: int = Depends(get_current_user)
) -> BoardResponse:
    return await board_service.update_board(board_id, board_data, current_user_id)

@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: int,
    board_service: BoardService = Depends(get_board_service),
    current_user_id: int = Depends(get_current_user)
):
    await board_service.delete_board(board_id, current_user_id)

@router.get("/{board_id}", response_model=BoardResponse)
async def get_board(
    board_id: int,
    board_service: BoardService = Depends(get_board_service),
    current_user_id: int = Depends(get_current_user)
) -> BoardResponse:
    return await board_service.get_board(board_id, current_user_id)

@router.get("", response_model=BoardList)
async def get_boards(
    cursor: Optional[str] = None,
    limit: int = 10,
    sort_by_posts: bool = False,
    board_service: BoardService = Depends(get_board_service),
    current_user_id: int = Depends(get_current_user)
) -> BoardList:
    boards, next_cursor = await board_service.get_boards(
        current_user_id, cursor, limit, sort_by_posts
    )
    return BoardList(
        items=boards,
        next_cursor=next_cursor
    ) 