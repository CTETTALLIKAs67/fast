# python -m uvicorn very_first:app --reload

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import hashlib

app = FastAPI()

templates = Jinja2Templates(directory="templates")

white_urls = ['/', '/login', '/register', '/profile']

@app.get("/", response_class=HTMLResponse) # перехват адреса http://localhost:8000/
def main_page(request: Request):
    return templates.TemplateResponse(request=request, name = "index.html")

@app.get('/register', response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name = 'register.html')

@app.post('/register', response_class=HTMLResponse)
def reg_user(request: Request, username: str = Form(...), name: str = Form(...), password: str = Form(...), password2: str = Form(...), ):
    users = load_data()
    users.append({
        "username": username,
        "name": name,
        "password": password 
    })
    save_data(users)

    return templates.TemplateResponse(
        'index.html',
        {'reauest': request, 'result': username, name, password, password2, 'items': users}
    )


@app.get('/login', response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name = 'login.html')

# @app.get('/profile', response_class=HTMLResponse)
# def login_page(request: Request):
#     return templates.TemplateResponse(request=request, name = 'profile.html')


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(request=request, name = '404.html', status_code=404)