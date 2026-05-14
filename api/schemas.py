from pydantic import BaseModel, EmailStr, Field

class ContactCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=5000)

class ContactResponse(BaseModel):
    id: int
    full_name: str
    email: str
    message: str
    
    class Config:
        from_attributes = True

class TelemetryEvent(BaseModel):
    event_type: str
    metadata: dict = {}
    duration_seconds: int = 0
