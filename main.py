from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

app = FastAPI()

DATABASE_URL = "sqlite:///./my_database.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

# ✅ ЭТОТ КЛАСС ДОЛЖЕН БЫТЬ — ОН ОПИСЫВАЕТ ФОРМАТ JSON, КОТОРЫЙ ВЫ ПРИСЫЛАЕТЕ
class UserCreate(BaseModel):
    name: str

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Сервер работает!"}

@app.get("/users")
def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return {"users": users}

# ✅ ПРАВИЛЬНАЯ ФУНКЦИЯ — ПРИНИМАЕТ UserCreate, А НЕ name: str
@app.post("/users")
def create_user(user: UserCreate):
    db = SessionLocal()
    new_user = User(name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return new_user

@app.get("/users/{user_id}")
def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    if user is None:
        return {"error": "Пользователь не найден"}
    return user

@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserCreate):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.id == user_id).first()
    if existing_user is None:
        db.close()
        return {"error": "Пользователь не найден"}
    existing_user.name = user.name
    db.commit()
    db.refresh(existing_user)
    db.close()
    return existing_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        db.close()
        return {"error": "Пользователь не найден"}
    db.delete(user)
    db.commit()
    db.close()
    return {"message": f"Пользователь {user_id} удалён"}