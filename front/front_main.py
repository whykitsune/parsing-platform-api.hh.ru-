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


count_of_pages = 0
cur_page = 0
vacancies_all = {}


@front_app.post('/vacancies/{path}', response_class=HTMLResponse)
def vacancies(
        request: Request,
        path: str,
        name: str = Form(default=''),
        city: str = Form(default='Россия'),
        salary: str = Form(default=None),
        prev: str = Form(default=None),
        next: str = Form(default=None),
        experience: str = Form(default=None),
        employment: list = Form(default=None),
        schedule: list = Form(default=None)
):
    params = {
        'vacancy': name,
        'city': city,
        'salary': salary
    }
    global count_of_pages, cur_page, vacancies_all

    if path == 'base':
        parsed_vacancies = requests.get('http://127.0.0.1:9000/get_vacancies', params=params)
        parsed_vacancies = parsed_vacancies.json()
        if not parsed_vacancies['ok']:
            return templates.TemplateResponse('vacancies.html', {'request': request,
                                                                 'ok': False})
        parsed_vacancies = parsed_vacancies['vacancies']
        if len(parsed_vacancies) // 20 == 0:
            count_of_pages = len(parsed_vacancies) // 20
        else:
            count_of_pages = len(parsed_vacancies) // 21
        vacancies_all = parsed_vacancies
        cur_page = 0

    if path == 'page':
        if prev == '<':
            if cur_page != 0:
                cur_page -= 1
        if next == '>':
            if cur_page != count_of_pages:
                cur_page += 1

    if path == 'filter':
        filters = {
            'experience': experience,
            'employment': employment,
            'schedule': schedule
        }
        filtered_vacancies = requests.get('http://127.0.0.1:9000/filter', params=filters)
        filtered_vacancies = filtered_vacancies.json()
        filtered_vacancies = filtered_vacancies['vacancies']
        if len(filtered_vacancies) // 20 == 0:
            count_of_pages = len(filtered_vacancies) // 20
        else:
            count_of_pages = len(filtered_vacancies) // 21
        vacancies_all = filtered_vacancies
        cur_page = 0

    return templates.TemplateResponse('vacancies.html', {'request': request,
                                                         'vacancies_all': vacancies_all,
                                                         'cur_page': cur_page,
                                                         'count_of_pages': count_of_pages,
                                                         'ok': True})
