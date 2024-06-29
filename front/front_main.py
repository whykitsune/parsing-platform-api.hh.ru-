from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

front_app = FastAPI()

front_app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@front_app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@front_app.post('/vacancies', response_class=HTMLResponse)
def vacancies(
        request: Request,
        name: str = Form(default=''),
        city: str = Form(default=None),
        salary: int = Form(default=None)
):
    return templates.TemplateResponse('vacancies.html', {'request': request, 'name': name, 'city': city, 'salary': salary})
