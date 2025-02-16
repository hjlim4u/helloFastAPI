from sqlalchemy.orm import Session
from models.board import Board
from schemas.board import BoardCreate, BoardUpdate, BoardResponse, BoardList
from typing import Optional, Tuple, List
from fastapi import HTTPException, status

class BoardService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_board(self, board_data: BoardCreate, user_id: int) -> BoardResponse:
        board = await Board.create_board(self.db, board_data, user_id)
        return BoardResponse.model_validate(board)
    
    async def update_board(self, board_id: int, board_data: BoardUpdate, user_id: int) -> BoardResponse:
        board = await Board.update_board(self.db, board_id, board_data, user_id)
        return BoardResponse.model_validate(board)
    
    async def delete_board(self, board_id: int, user_id: int) -> None:
        await Board.delete_board(self.db, board_id, user_id)
    
    async def get_board(self, board_id: int, user_id: int) -> BoardResponse:
        board = await Board.get_accessible_board(self.db, board_id, user_id)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found"
            )
        
        if not board.public and board.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this board"
            )
            
        return BoardResponse.model_validate(board)
    
    async def get_boards(
        self, 
        user_id: int, 
        cursor: Optional[str] = None,
        limit: int = 10,
        sort_by_posts: bool = False
    ) -> Tuple[List[BoardResponse], Optional[str]]:
        boards, next_cursor = await Board.get_boards(
            self.db, 
            user_id, 
            cursor, 
            limit,
            sort_by_posts
        )
        return [BoardResponse.model_validate(board) for board in boards], next_cursor 