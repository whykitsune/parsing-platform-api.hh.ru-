import requests
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
        city: str = Form(default='Россия'),
        salary: str = Form(default=None)
):
    params = {
        'vacancy': name,
        'city': city,
        'salary': salary
    }
    parsed_vacancies = requests.post('http://127.0.0.1:9000/get_vacancies', json=params)
    parsed_vacancies = parsed_vacancies.json()
    print(parsed_vacancies)
    parsed_vacancies = parsed_vacancies['vacancies']

    return templates.TemplateResponse('vacancies.html', {'request': request, 'parsed_vacancies': parsed_vacancies})
