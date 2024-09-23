from datetime import date
from pydantic import BaseModel

class UserSchema(BaseModel):
    email: str
    password: str

class EmployeeSchema(BaseModel):
    name:str
    email:str
    phone:str
    dob:date
    address:str
    position:str
