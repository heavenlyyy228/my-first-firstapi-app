# FastAPI CRUD API

Простой REST API для управления пользователями на FastAPI.

## Технологии
- Python 3.11
- FastAPI
- SQLAlchemy (ORM)
- SQLite
- Pydantic

## Функционал
- GET /users — список всех пользователей
- GET /users/{id} — получить одного пользователя
- POST /users — создать пользователя
- PUT /users/{id} — обновить пользователя
- DELETE /users/{id} — удалить пользователя

## Запуск локально
```bash
git clone https://github.com/ВАШ_ЛОГИН/название-репозитория.git
cd название-репозитория
python -m venv venv
source venv/bin/activate  # для Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
