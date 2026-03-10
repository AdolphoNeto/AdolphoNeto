from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str = "user"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class ConferenceBase(BaseModel):
    name: str
    description: Optional[str] = None

class ConferenceCreate(ConferenceBase):
    pass

class Conference(ConferenceBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "processing"
    total_records: int = 0
    matches: int = 0
    divergences: int = 0
    duplicates: int = 0
    log2_count: int = 0
    log3_count: int = 0
    cubo_count: int = 0

class ValidationResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conference_id: str
    source_type: str
    record_id: str
    status: str
    data: Dict[str, Any]
    issues: List[str] = []
    matched_records: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DashboardStats(BaseModel):
    total_conferences: int
    total_records_processed: int
    total_divergences: int
    total_duplicates: int
    recent_conferences: List[Conference]
    divergence_rate: float
    duplicate_rate: float