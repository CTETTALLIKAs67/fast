# python -m uvicorn very_first:app --reload

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
import json

import hashlib

app = FastAPI()

templates = Jinja2Templates(directory="templates")

white_urls = ['/', '/login', '/register', '/profile']
DATA_FILE = Path("users.json")

def load_user() -> list:
    """Читает JSON. Если файла нет — возвращает пустой список."""
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_user(data: list) -> None:
    """Записывает список в JSON."""
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )

@app.get("/", response_class=HTMLResponse) # перехват адреса http://localhost:8000/
def main_page(request: Request):
    return templates.TemplateResponse(request=request, name = "index.html")

@app.get('/register', response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name = 'register.html')

@app.post('/register', response_class=HTMLResponse)
def register(
    request: Request, 
    username: str = Form(...), 
    name: str = Form(...), 
    password: str = Form(...), 
    password2: str = Form(...), 
):
    username = username.strip()
    users = load_user()
    error = None

    if not username or not name or not password or not password2:
        error = 'Заполните все поля обозначенные *'
    elif password != password2:
        error = 'Введите одинаковые пароли'
    elif any(u['username'] == username for u in users):
        error = 'Введённый логин уже занят'

    if error:
        return templates.TemplateResponse(
            request=request,
            name='register.html',
            context= {'error': error},
            status_code=400
        )
    
    users.append({
        "username": username,
        "name": name,
        "password": password 
    })
    save_user(users)

    return RedirectResponse('/login', status_code=303)


@app.get('/login', response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name = 'login.html', context={'registered': True})

# @app.get('/profile', response_class=HTMLResponse)
# def login_page(request: Request):
#     return templates.TemplateResponse(request=request, name = 'profile.html')


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(request=request, name = '404.html', status_code=404)