from sqlalchemy import Column,Date
from sqlalchemy.types import String, Integer

from database import Base


#Tài khoản
class UserModel(Base):
    __tablename__="user"
    id = Column(Integer, primary_key=True, index=True)
    email=Column(String(45),unique=True)
    password=Column(String(45))
    created_at=Column(Date)
    updated_at=Column(Date)
    deleted_at=Column(Date)
#Nhân viên
class EmployeeModel(Base):
    __tablename__="employee"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(6), index=True)
    name=Column(String(45))
    email=Column(String(45),unique=True)
    phone=Column(String,unique=True)
    dob=Column(Date)
    address=Column(String(4))
    position=Column(String(45))
    status=Column(Integer)
    created_at=Column(Date)
    updated_at=Column(Date)
    deleted_at=Column(Date)