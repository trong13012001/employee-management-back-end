from fastapi import Depends, APIRouter, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from model import UserModel, EmployeeModel
from database import SessionLocal, engine
from schema import EmployeeSchema
import model
from datetime import datetime
import uuid
from auth.auth_handler import JWTBearer
from fastapi import Header
from auth.auth_handler import decodeJWT

router = APIRouter(prefix="/api/v1/employee")
model.Base.metadata.create_all(bind=engine)


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def generate_employee_code(db: Session):
    latest_code = db.query(func.max(EmployeeModel.code)).filter(EmployeeModel.code.like('EML%')).scalar()
    if latest_code:
        latest_number = int(latest_code[3:])  
        new_number = latest_number + 1
    else:
        new_number = 1

    # Format the new number with leading zeros
    new_code = f"EML{str(new_number).zfill(3)}"
    return new_code


@router.post("", summary="Tạo nhân viên", dependencies=[Depends(JWTBearer())])
def create_employee(
    employeeSchema: EmployeeSchema,
    db: Session = Depends(get_database_session),
):
    # Check for unique fields (phone, email)
    phone_exist = db.query(EmployeeModel).filter(EmployeeModel.phone == employeeSchema.phone).first()
    email_exist = db.query(EmployeeModel).filter(EmployeeModel.email == employeeSchema.email).first()

    if phone_exist:
        raise HTTPException(status_code=400, detail="Số điện thoại đã tồn tại")
    if email_exist:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")

    new_code = generate_employee_code(db)

    new_employee = EmployeeModel(
        code=new_code,
        name=employeeSchema.name,
        phone=employeeSchema.phone,
        email=employeeSchema.email,
        position=employeeSchema.position,
        dob=employeeSchema.dob,
        address=employeeSchema.address,
        status=1,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return {"message": "Tạo nhân viên thành công", "employee_code": new_code}
@router.put("/{employee_id}", summary="Cập nhật nhân viên", dependencies=[Depends(JWTBearer())])
def update_employee(
    employee_id: str,
    employee_update: EmployeeSchema,
    db: Session = Depends(get_database_session),
):
    existing_employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
    if not existing_employee:
        raise HTTPException(status_code=404, detail="Nhân viên không tồn tại")

    # Check for unique fields (phone, email)
    phone_exist = db.query(EmployeeModel).filter(EmployeeModel.phone == employee_update.phone, EmployeeModel.id != employee_id).first()
    email_exist = db.query(EmployeeModel).filter(EmployeeModel.email == employee_update.email, EmployeeModel.id != employee_id).first()

    if phone_exist:
        raise HTTPException(status_code=400, detail="Số điện thoại đã tồn tại")
    if email_exist:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")

    existing_employee.name = employee_update.name
    existing_employee.phone = employee_update.phone
    existing_employee.email = employee_update.email
    existing_employee.position = employee_update.position
    existing_employee.dob = employee_update.dob
    existing_employee.address = employee_update.address
    existing_employee.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    db.commit()
    db.refresh(existing_employee)

    return {"message": "Cập nhật nhân viên thành công", "employee_code": existing_employee.code}
@router.delete("/{employee_id}", summary="Xóa nhân viên", dependencies=[Depends(JWTBearer())])
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_database_session),
):
    existing_employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
    if not existing_employee:
        raise HTTPException(status_code=404, detail="Nhân viên không tồn tại")

    existing_employee.status = 0
    existing_employee.deleted_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    db.commit()
    db.refresh(existing_employee)

    return {"message": "Xóa nhân viên thành công", "employee_code": existing_employee.code}
@router.get("", summary="Lấy tất cả nhân viên", dependencies=[Depends(JWTBearer())])
def get_employees(
    page: int = Query(1, description="Page number"),
    limit: int = Query(10, description="Number of items per page"),
    db: Session = Depends(get_database_session),
):
    # Calculate the offset based on the page and limit
    offset = (page - 1) * limit

    # Query the employees with pagination
    employees = db.query(EmployeeModel).filter(EmployeeModel.status == 1).offset(offset).limit(limit).all()

    return employees

@router.get("/{employee_id}", summary="Lấy một nhân viên", dependencies=[Depends(JWTBearer())])
def get_employee_by_id(
    employee_id: str,
    db: Session = Depends(get_database_session),
):
    employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Nhân viên không tồn tại")
    return employee
@router.get("/search", summary="Tìm kiếm nhân viên", dependencies=[Depends(JWTBearer())])
def search_employees(
    keyword: str = Query(None, description="Từ khóa tìm kiếm"),
    db: Session = Depends(get_database_session),
):
    employees = db.query(EmployeeModel).filter(EmployeeModel.name.like(f"%{keyword}%"), EmployeeModel.status == 1).all()
    return employees