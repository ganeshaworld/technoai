import hashlib
import hmac
import base64
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.config import settings
from backend.app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def hash_password(password: str) -> str:
    """Secure password hashing using salted SHA-256 with key derivation."""
    salt = settings.SECRET_KEY[:16].encode("utf-8")
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return derived.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hmac.compare_digest(hash_password(plain_password), hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None

async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    from backend.app.db.models import User, UserProfile
    
    # If no token provided, return or create a default guest/demo executive user for seamless zero-barrier usage
    if not token:
        # Check if default demo user exists
        stmt = select(User).where(User.email == "demo@technopie.ai")
        result = await db.execute(stmt)
        user = result.scalars().first()
        if not user:
            user = User(
                email="demo@technopie.ai",
                hashed_password=hash_password("DemoPassword123!"),
                is_active=True,
                is_verified=True,
                is_superuser=False
            )
            db.add(user)
            await db.flush()
            profile = UserProfile(
                user_id=user.id,
                full_name="Alexander Vance",
                preferred_name="Alexander",
                profession="Founder & Managing Director",
                work_description="Directing corporate strategy, international expansion and investment portfolio.",
                preferred_language="en",
                timezone="UTC",
                productivity_goals=["Zero inbox by 6 PM", "Morning schedule briefings", "High-priority meeting prep"],
                ai_tone_preference="executive",
                onboarding_completed=True
            )
            db.add(profile)
            await db.commit()
            await db.refresh(user)
        return user

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

async def get_current_user(user = Depends(get_current_user_optional)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user
