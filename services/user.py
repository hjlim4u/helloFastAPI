from typing import Optional
from datetime import timedelta, datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from redis import Redis
from jose import jwt, JWTError
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import redis

from models.user import User
from schemas.user import UserCreate, UserLogin, Token
from core.config import settings

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: AsyncSession, redis_client: Redis):
        self.db = db
        self.redis_client = redis_client

    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def _verify_and_refresh_session(self, session_id: str, email: str) -> bool:
        """세션 유효성 검사 및 갱신"""
        session_key = f"session:{session_id}"
        session_email = self.redis_client.get(session_key)
        
        if not session_email or session_email.decode() != email:
            return False
            
        # 세션 만료 시간 갱신
        self.redis_client.expire(session_key, settings.SESSION_EXPIRE_MINUTES * 60)  # 분을 초로 변환
        return True

    def refresh_token(self, token: str) -> Token:
        """토큰 갱신"""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            email = payload.get("sub")
            session_id = payload.get("session")
            
            if not email or not session_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token content"
                )
                
            # 세션 유효성 검사 및 갱신
            if not self._verify_and_refresh_session(session_id, email):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session expired or invalid"
                )
            
            # 새로운 토큰 생성
            new_session_id = str(uuid.uuid4())
            self.redis_client.setex(f"session:{new_session_id}", 1800, email)
            
            # 이전 세션 삭제
            self.redis_client.delete(f"session:{session_id}")
            
            # 새 토큰 발급
            access_token = self._create_access_token(
                data={"sub": email, "session": new_session_id}
            )
            return Token(access_token=access_token)
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

    async def create_user(self, user_data: UserCreate) -> Token:
        # 사용자 생성
        user = await User.create_user(self.db, user_data)
        
        # 세션 ID 생성 및 Redis에 저장
        session_id = str(uuid.uuid4())
        session_key = f"session:{session_id}"
        self.redis_client.setex(
            session_key,
            settings.SESSION_EXPIRE_MINUTES * 60,  # 분을 초로 변환
            user.email
        )
        
        # 액세스 토큰 생성
        access_token = self._create_access_token(
            data={"sub": user.email, "session": session_id}
        )
        
        return Token(access_token=access_token, token_type="bearer")

    async def authenticate_user(self, user_data: UserLogin) -> Token:
        # 데이터 레이어를 통한 사용자 인증
        user = await User.authenticate_user(
            self.db, 
            user_data.email, 
            user_data.password
        )
        
        # 세션 생성 및 Redis에 저장
        session_id = str(uuid.uuid4())
        self.redis_client.setex(
            f"session:{session_id}", 
            settings.SESSION_EXPIRE_MINUTES * 60,  # 분을 초로 변환
            user.email
        )
        
        access_token = self._create_access_token(
            data={"sub": user.email, "session": session_id}
        )
        return Token(access_token=access_token)

    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    async def logout_user(self, session_id: str) -> dict:
        """사용자 로그아웃 처리"""
        try:
            session_key = f"session:{session_id}"
            logger.debug(f"Checking session key: {session_key}")
            
            # Redis 연결 확인
            if not self.redis_client.ping():
                logger.error("Redis connection failed")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Session service unavailable"
                )
            
            # 세션 존재 여부 확인
            if not self.redis_client.exists(session_key):
                logger.warning(f"Session not found: {session_key}")
                # 세션이 없어도 성공적으로 로그아웃 처리
                return {"message": "Successfully logged out"}
            
            # 세션 삭제
            self.redis_client.delete(session_key)
            logger.info(f"Successfully deleted session: {session_key}")
            
            return {"message": "Successfully logged out"}
            
        except redis.RedisError as e:
            logger.error(f"Redis error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Session service error"
            )
