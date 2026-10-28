from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.models.profile import CandidateProfile
from backend.schemas.auth import UserRegister, UserLogin, Token, UserOut
from backend.utils.security import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Registers a new user account and creates a default candidate profile."""
    email_clean = str(user_data.email).lower().strip()
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    user = User(
        email=email_clean,
        name=user_data.name,
        password_hash=get_password_hash(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create default candidate profile
    profile = CandidateProfile(
        user_id=user.id,
        full_name=user.name,
        education="B.Tech in Computer Science",
        skills=["Java", "SQL", "HTML", "CSS", "Python"],
        programming_languages=["Java", "Python"],
        experience_level="Fresher",
        target_role="Java Developer",
        preferred_interview_type="Technical",
        preferred_difficulty="Medium"
    )
    db.add(profile)
    db.commit()

    return user

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user credentials and returns a JWT access token."""
    email_clean = str(login_data.email).lower().strip()
    user = db.query(User).filter(User.email == email_clean).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_access_token(data={"sub": user.id, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "user_name": user.name,
        "email": user.email
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieves details of the currently authenticated user."""
    return current_user
