from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.utils.seed_data import seed_demo_candidate_data

router = APIRouter(prefix="/api/seed", tags=["Seed Demo Data"])

@router.post("/demo-data", status_code=status.HTTP_201_CREATED)
def seed_demo(db: Session = Depends(get_db)):
    """Seeds database with a pre-populated Demo Candidate, completed interview, and evaluation report."""
    return seed_demo_candidate_data(db)
