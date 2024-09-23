from fastapi import Depends, APIRouter,HTTPException,Form
from sqlalchemy import exists
from sqlalchemy.orm import Session
from model import StatusModel,TaskModel
from database import SessionLocal, engine
from schema import StatusSchema
import model
from datetime import datetime
import uuid
from auth.auth_handler import JWTBearer

router = APIRouter(prefix="/api/v1/status")  
model.Base.metadata.create_all(bind=engine)


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
custome_uuid=str(uuid.uuid4()).replace('-', '')[:8]

#Thêm loại sản phẩm
@router.post("/create", summary="Tạo trạng thái",dependencies=[Depends(JWTBearer().has_role([1]))])
async def create_status(
    statusSchema: StatusSchema,
    db: Session = Depends(get_database_session),
):
    status_exists = db.query(exists().where(StatusModel.name == statusSchema.name, StatusModel.deleted_at == None)).scalar()
    
    if status_exists:
        raise HTTPException(status_code=400, detail="Trạng thái đã tồn tại")

    # Create a new ProductSchema instance and add it to the database
    new_status = StatusModel(
        id=str(uuid.uuid4()).replace('-', '')[:8],
        name=statusSchema.name,
        color=statusSchema.color,
        background_color=statusSchema.background_color,
        is_default=False,
        is_completed=statusSchema.is_completed,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M")
    )

    db.add(new_status)
    db.commit()
    db.refresh(new_status)
    return {"message": "Tạo trạng thái thành công"}

# Sủa loại sản phẩm
@router.patch("/update/{status_id}", summary="Cập nhật trạng thái",dependencies=[Depends(JWTBearer().has_role([1]))])
async def update_status(
    status_id: str,
    status_update: StatusSchema,
    db: Session = Depends(get_database_session),
):
    existing_status = db.query(StatusModel).filter(StatusModel.id == status_id).first()
    if not existing_status:
        raise HTTPException(status_code=404, detail="Trạng thái không tồn tại!")
    existing_status.name = status_update.name
    existing_status.color = status_update.color
    existing_status.background_color = status_update.background_color
    existing_status.is_completed = status_update.is_completed
    existing_status.is_default = False
    existing_status.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    existing_status.deleted_at =None

  
    db.commit()
    db.refresh(existing_status)

    return {"message": "Chỉnh sửa trạng thái thành công"}

#Hoàn tác xoá đăng nhập
@router.patch("/undo_delete/{status_id}", summary="Hoàn tác xóa trạng thái",dependencies=[Depends(JWTBearer().has_role([1]))])
async def undo_delete_status(
    status_id: str,
    db: Session = Depends(get_database_session)):
    existing_status= db.query(StatusModel).filter(StatusModel.id == status_id).first()
    if not existing_status:
        raise HTTPException(status_code=404, detail=f"Trạng thái không tồn tại!")
    existing_status.deleted_at = None

    db.commit()

    return {"message": "Hoàn tác xoá trạng thái thành công"}
#Đặt làm mặc định
@router.patch("/default/{status_id}", summary="Đặt làm mặc định", dependencies=[Depends(JWTBearer().has_role([1]))])
async def set_default_status(status_id: str, db: Session = Depends(get_database_session)):
    existing_status = db.query(StatusModel).filter(StatusModel.id == status_id).first()
    if not existing_status:
        raise HTTPException(status_code=404, detail="Trạng thái không tồn tại!")

    db.query(StatusModel).update({StatusModel.is_default: False})
    
    existing_status.is_default = True
    
    db.commit()

    return {"message": "Đặt trạng thái mặc định thành công"}

#Lấy tất cả loại sản phẩm
@router.get("", summary="Lấy tất cả trạng thái",dependencies=[Depends(JWTBearer().has_role([1,2,3]))])
def get_status(
    db: Session = Depends(get_database_session),
):
    statuses = (
    db.query(StatusModel).filter(StatusModel.deleted_at==None).all()

    )
    return statuses
@router.get("/{status_id}", summary="Lấy một trạng thái",dependencies=[Depends(JWTBearer().has_role([1]))])
def get_status_by_id(
    status_id: str,
    db: Session = Depends(get_database_session),
):
    statuses = (
    db.query(StatusModel).filter(StatusModel.id==status_id).first()
    )
    return  statuses
#Xóa loại sản phẩm
@router.delete("/delete/{status_id}", summary="Xóa trạng thái", dependencies=[Depends(JWTBearer().has_role([1]))])
async def delete_status(status_id: str, db: Session = Depends(get_database_session)):
    existing_status = db.query(StatusModel).filter(StatusModel.id == status_id).first()
    if not existing_status:
        raise HTTPException(status_code=404, detail="Trạng thái không tồn tại!")
    
    if existing_status.name == "Cần làm":
        raise HTTPException(status_code=400, detail="Không thể xóa trạng thái mặc định")
    
    associated_tasks = db.query(TaskModel).filter(TaskModel.status_id == status_id).first()
    if associated_tasks:
        raise HTTPException(status_code=400, detail="Không thể xóa trạng thái đang được sử dụng trong công việc!")
    
    # Delete the status immediately
    db.delete(existing_status)
    db.commit()

    return {"message": "Xoá trạng thái thành công"}