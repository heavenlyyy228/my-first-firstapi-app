from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

DATABASE_URL = "sqlite:///./habits.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Модели
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    habits = relationship("Habit", back_populates="owner")

class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, default="")
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="habits")

# Pydantic схемы
class UserCreate(BaseModel):
    username: str
    password: str

class HabitCreate(BaseModel):
    title: str
    description: Optional[str] = ""

class HabitResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

Base.metadata.create_all(bind=engine)

# Шаблоны
templates = Jinja2Templates(directory="templates")

# Главная страница
@app.get("/", response_class=HTMLResponse)
def frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Регистрация
@app.post("/register")
def register(user: UserCreate):
    db = SessionLocal()
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return {"message": "User created", "user_id": new_user.id}

# Логин
@app.post("/login")
def login(user: UserCreate):
    db = SessionLocal()
    db_user = db.query(User).filter(
        User.username == user.username,
        User.password == user.password
    ).first()
    db.close()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": db_user.id}

# Создать привычку
@app.post("/habits/{user_id}")
def create_habit(user_id: int, habit: HabitCreate):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    new_habit = Habit(title=habit.title, description=habit.description, user_id=user_id)
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)
    db.close()
    return new_habit

# Получить привычки пользователя
@app.get("/habits/{user_id}", response_model=List[HabitResponse])
def get_habits(user_id: int):
    db = SessionLocal()
    habits = db.query(Habit).filter(Habit.user_id == user_id).all()
    db.close()
    return habits

# Переключить статус привычки
@app.put("/habits/{habit_id}/complete")
def complete_habit(habit_id: int):
    db = SessionLocal()
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        db.close()
        raise HTTPException(status_code=404, detail="Habit not found")
    habit.completed = not habit.completed
    db.commit()
    db.refresh(habit)
    db.close()
    return habit

# Удалить привычку
@app.delete("/habits/{habit_id}")
def delete_habit(habit_id: int):
    db = SessionLocal()
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        db.close()
        raise HTTPException(status_code=404, detail="Habit not found")
    db.delete(habit)
    db.commit()
    db.close()
    return {"message": "Habit deleted"}


