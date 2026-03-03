from fastapi import APIRouter
from app.services.services import Services
from pydantic import BaseModel

router = APIRouter()

class InputText(BaseModel):
    text: str
    
services = Services()

@router.get("/")
async def read_root():
    return services.get_welcome_message()
    
@router.post("/api/v1/predict")
async def return_predict(user_input: InputText):
    return services.get_model_predict(user_input.text)