from sqlalchemy import Column, Integer, String, DateTime, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from core.database import Base
from core.security import get_password_hash, verify_password
from schemas.user import UserCreate
from fastapi import HTTPException, status

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    boards = relationship("Board", back_populates="owner")
    posts = relationship("Post", back_populates="author")

    @classmethod
    async def create_user(cls, db: AsyncSession, user_data: UserCreate) -> "User":
        # 이메일 중복 확인
        if await cls.get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # 새 사용자 생성
        db_user = cls(
            fullname=user_data.fullname,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password)
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @classmethod
    async def get_user_by_email(cls, db: AsyncSession, email: str) -> "User":
        query = select(cls).where(cls.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def authenticate_user(cls, db: AsyncSession, email: str, password: str) -> "User":
        user = await cls.get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        return user