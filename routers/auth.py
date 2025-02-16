from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from jose import JWTError, jwt
from core.config import settings

from core.database import get_db
from core.config import settings
from schemas.user import UserCreate, UserLogin, Token
from services.user import UserService
from models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db, redis_client)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
        user = await User.get_user_by_email(db, email)
        if user is None:
            raise credentials_exception
            
        return user.id
    except JWTError:
        raise credentials_exception

@router.post("/signup", response_model=Token)
async def signup(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.create_user(user_data)

# @router.post("/login", response_model=Token)
# async def login(
#     user_data: UserLogin,
#     user_service: UserService = Depends(get_user_service)
# ):
#     return user_service.authenticate_user(user_data)

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        session_id = payload.get("session")
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )
        return await user_service.logout_user(session_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login", response_model=Token)
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.authenticate_user(UserLogin(
        email=form_data.username,
        password=form_data.password
    ))

@router.post("/refresh", response_model=Token)
async def refresh_token(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
):
    return user_service.refresh_token(token)