from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    confirm_password: str = Field(min_length=6, max_length=128)
    user_type: str | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AnalyzeRequest(BaseModel):
    user_id: int
    mood: str = ""
    message: str = Field(min_length=1)
    count: int = Field(default=6, ge=1, le=8)

class MoodRequest(BaseModel):
    user_id: int
    mood: str
    message: str

class GameRequest(BaseModel):
    user_id: int
    activity_id: int | None = None
    game_name: str
    score: int = Field(ge=0)
    duration: int = Field(ge=0)
