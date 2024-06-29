from fastapi import FastAPI
import requests
import json
import time
import re
from src.models import VacanciesTable
from src.database import session_factory
from src.query import create_tables

app = FastAPI()


# @app.get('/get_vacancy')
def get_vacancies(
        vacancy: str = '',
        city: str = 'Россия',
        salary: str = None
):
    create_tables()
    url_areas = 'https://api.hh.ru/areas'
    res = requests.get(url_areas)
    res.raise_for_status()
    res = json.loads(res.text)
    areas = {'Россия': 113}
    if city:
        for area in res[0]['areas']:
            areas[area['name']] = area['id']
            if area['areas']:
                cur_area = area['areas']
                for cur_city in cur_area:
                    areas[cur_city['name']] = cur_city['id']
        for key, value in areas.items():
            if str(city).lower() == key.lower():
                city = areas[key]

    url = 'https://api.hh.ru/vacancies'
    params = {
        'text': f'{vacancy}',
        'area': city,
        'salary': salary,
        'per_page': 100
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    response = json.loads(response.text)
    vacancies = []
    for page in range(response['pages']):
        params = {
            'text': f'{vacancy}',
            'area': city,
            'salary': salary,
            'per_page': 100,
            'page': page
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        response = json.loads(response.text)
        vacancies += response['items']
        time.sleep(1)
    out_vacancies = []
    c=0
    for item in vacancies:
        out_vacancy = {}
        item_id = item['id']
        url_vacancy = f'https://api.hh.ru/vacancies/{item_id}'
        response_vacancy = requests.get(url_vacancy)
        response_vacancy.raise_for_status()
        response_vacancy = json.loads(response_vacancy.text)
        out_vacancy['name'] = response_vacancy['name']
        out_vac_salary = ''
        if response_vacancy['salary']:
            vac_salary = response_vacancy['salary']
            if vac_salary['from'] and vac_salary['to']:
                vac_salary_from = vac_salary['from']
                vac_salary_to = vac_salary['to']
                out_vac_salary += f'От {vac_salary_from} до {vac_salary_to} '
            if vac_salary['from'] and not vac_salary['to']:
                vac_salary_from = vac_salary['from']
                out_vac_salary += f'От {vac_salary_from} '
            if not vac_salary['from'] and vac_salary['to']:
                vac_salary_to = vac_salary['to']
                out_vac_salary += f'До {vac_salary_to} '
            out_vac_salary += vac_salary['currency']
        else:
            out_vac_salary = 'Уровень дохода не указан'
        out_vacancy['salary'] = out_vac_salary
        employer = response_vacancy['employer']
        out_vacancy['employer'] = employer['name']
        experience = response_vacancy['experience']
        out_vacancy['experience'] = experience['name']
        employment = response_vacancy['employment']
        out_vacancy['employment'] = employment['name']
        vac_area = response_vacancy['area']
        out_vacancy['area'] = vac_area['name']
        vac_skills = []
        key_skills = response_vacancy['key_skills']
        if key_skills:
            for i in range(len(key_skills)):
                vac_skills.append(key_skills[i]['name'])
        vac_skills_str = ''
        for cur_skill in vac_skills:
            vac_skills_str += f'{cur_skill} '
        out_vacancy['key_skills'] = vac_skills_str
        description = response_vacancy['description']
        pattern = re.compile('<.*?>')
        description = re.sub(pattern, '', description)
        out_vacancy['description'] = description
        out_vacancy['url'] = response_vacancy['alternate_url']
        out_vacancies.append(out_vacancy)
        c += 1
        if c == 10:
            break

    with session_factory() as session:
        for cur_vacancy in out_vacancies:
            vacancy_to_table = VacanciesTable(
                name=cur_vacancy['name'],
                salary=cur_vacancy['salary'],
                employer=cur_vacancy['employer'],
                experience=cur_vacancy['experience'],
                employment=cur_vacancy['employment'],
                area=cur_vacancy['area'],
                key_skills=cur_vacancy['key_skills'],
                description=cur_vacancy['description'],
                url=cur_vacancy['url']
            )

            session.add(vacancy_to_table)
            session.commit()

    return {'ok': True, 'response': out_vacancies}


@app.post('/get_vacancies')
def get_vacancies_from_db(
        vacancy: str = '',
        city: str = 'Россия',
        salary: str = None
):
    get_vacancies(vacancy, city, salary)
    with session_factory() as session:
        vacancies = session.query(VacanciesTable).all()
        out_vacancies = []
        for vacancy in vacancies:
            vacancy_dict = dict()
            vacancy_dict['name'] = vacancy.name
            vacancy_dict['salary'] = vacancy.salary
            vacancy_dict['employer'] = vacancy.employer
            vacancy_dict['experience'] = vacancy.experience
            vacancy_dict['employment'] = vacancy.employment
            vacancy_dict['area'] = vacancy.area
            vacancy_dict['key_skills'] = vacancy.key_skills
            vacancy_dict['description'] = vacancy.description
            vacancy_dict['url'] = vacancy.url
            out_vacancies.append(vacancy_dict)

        return {'vacancies': out_vacancies}


# print(get_vacancies(city='Кострома'))
# print(get_vacancies_from_db())
