from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class Register(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str
    user_type: Optional[str] = "student"

    stress_sources: List[str] = Field(default_factory=list)
    other_stress: Optional[str] = ""
    meditation_time: Optional[str] = "5"
    recent_feeling: Optional[str] = ""
    meditation_experience: Optional[str] = ""
    goals: List[str] = Field(default_factory=list)
    support_preference: Optional[str] = ""
    language: Optional[str] = "English"


class Login(BaseModel):
    email: EmailStr
    password: str


class Analyze(BaseModel):
    user_id: int
    message: str
    count: int = 1


class Chat(BaseModel):
    user_id: int
    message: str
    language: str = "English"


class Profile(BaseModel):
    full_name: str


class Prefs(BaseModel):
    language: Optional[str] = None
    meditation_time: Optional[str] = None


class Forgot(BaseModel):
    email: EmailStr


class PasswordChange(BaseModel):
    user_id: int
    old_password: str
    new_password: str