from fastapi import Depends, Header,APIRouter,HTTPException,UploadFile,File
from sqlalchemy.orm import Session
from auth.auth_handler import decodeJWT
from model import UserModel
from database import SessionLocal, engine
import model
from auth.auth_handler import JWTBearer
from datetime import datetime

router = APIRouter(prefix="/api/v1/user")  
model.Base.metadata.create_all(bind=engine)


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/self", summary="Lấy thông tin bản thân", dependencies=[Depends(JWTBearer())])
async def get_user_self(
    authorization: str = Header(...),
    db: Session = Depends(get_database_session),
):
    user = decodeJWT(authorization.split()[1])
    email = user.get("email")

    user_data = db.query(UserModel).filter(UserModel.email == email).first()

    if user_data:
        return {
            "id": user_data.id,
            "email": user_data.email,
        }
    else:
        return {"error": "User not found"}, 404