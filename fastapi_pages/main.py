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
app.add_middleware(SessionMiddleware, secret_key="секретная-строка-для-подписи-cookie")

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

@app.get("/", response_class=HTMLResponse)
def main_page(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse(request=request,context = {'user': user} ,name = "index.html")

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

    return RedirectResponse('/login?registered=1', status_code=303)


@app.get('/login', response_class=HTMLResponse)
def login_page(request: Request):
    registered = request.query_params.get('registered') == '1'
    return templates.TemplateResponse(
        request=request,
        name = 'login.html',
        context = {'registered': registered},
    )

@app.post('/login', response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    username = username.strip()
    error = None
    if not username or not password:
        error = 'Введите логин или пароль'
    else:
        user = None
        for u in load_user():
            if u['username'] == username:
                user = u
                break
        if user is None or user['password'] != password:
            error = 'Неверный логин или пароль'
    
    if error:
        return templates.TemplateResponse(
            request = request,
            name = 'login.html',
            context = {'error': error, 'username': username},
            status_code = 400
        )
    
    request.session['user'] = {'username': user['username'], 'name': user['name']}
    return RedirectResponse('/profile', status_code = 303)

@app.get('/profile', response_class=HTMLResponse)
def login_page(request: Request):
    user = request.session.get('user')
    if user is None:
        return templates.TemplateResponse(
            request=request,
            name = '403.html',
            context = {},
            status_code = 40
        )
    
    return templates.TemplateResponse(
        request = request,
        name = 'profile.html',
        context = {'user': user}
    )

@app.get('/logout')
def logout(request: Request):
    request.session.clear()
    return RedirectResponse('/', status_code=303)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(request=request, name = '404.html', status_code=404)