from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List, Dict, Any

from backend.app.db.session import get_db
from backend.app.db.models import User, UserProfile
from backend.app.core.security import (
    hash_password, verify_password, create_access_token, get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication & Profile"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    profession: Optional[str] = "Executive"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class OnboardingRequest(BaseModel):
    profession: str
    work_description: str
    preferred_language: str = "en"
    timezone: str = "UTC"
    productivity_goals: List[str] = []
    ai_tone_preference: str = "executive"

@router.post("/register")
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == payload.email)
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    new_user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        is_active=True,
        is_verified=True
    )
    db.add(new_user)
    await db.flush()

    profile = UserProfile(
        user_id=new_user.id,
        full_name=payload.full_name,
        preferred_name=payload.full_name.split(" ")[0],
        profession=payload.profession,
        onboarding_completed=False
    )
    db.add(profile)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token({"sub": new_user.id, "email": new_user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": payload.full_name,
            "onboarding_completed": False
        }
    }

@router.post("/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == payload.email)
    user = (await db.execute(stmt)).scalars().first()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token({"sub": user.id, "email": user.email})
    # Fetch profile
    stmt_prof = select(UserProfile).where(UserProfile.user_id == user.id)
    profile = (await db.execute(stmt_prof)).scalars().first()

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": profile.full_name if profile else "Executive User",
            "onboarding_completed": profile.onboarding_completed if profile else True
        }
    }

@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(UserProfile).where(UserProfile.user_id == user.id)
    profile = (await db.execute(stmt)).scalars().first()
    return {
        "id": user.id,
        "email": user.email,
        "full_name": profile.full_name if profile else "Alexander Vance",
        "preferred_name": profile.preferred_name if profile else "Alexander",
        "profession": profile.profession if profile else "Founder & CEO",
        "work_description": profile.work_description if profile else "",
        "preferred_language": profile.preferred_language if profile else "en",
        "timezone": profile.timezone if profile else "UTC",
        "productivity_goals": profile.productivity_goals if profile else [],
        "ai_tone_preference": profile.ai_tone_preference if profile else "executive",
        "onboarding_completed": profile.onboarding_completed if profile else False
    }

@router.put("/profile/onboarding")
async def complete_onboarding(
    payload: OnboardingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(UserProfile).where(UserProfile.user_id == user.id)
    profile = (await db.execute(stmt)).scalars().first()
    if not profile:
        profile = UserProfile(user_id=user.id, full_name="Executive User")
        db.add(profile)

    profile.profession = payload.profession
    profile.work_description = payload.work_description
    profile.preferred_language = payload.preferred_language
    profile.timezone = payload.timezone
    profile.productivity_goals = payload.productivity_goals
    profile.ai_tone_preference = payload.ai_tone_preference
    profile.onboarding_completed = True

    await db.commit()
    return {"status": "success", "message": "Executive onboarding completed."}
