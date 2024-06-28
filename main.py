from fastapi import FastAPI
import requests
from pydantic import BaseModel
import json
import time
import re

app = FastAPI()


# @app.get('/get_vacancy')
def get_vacancies(
        vacancy: str = '',
        city: str = None,
        salary: int = None
):
    url_areas = 'https://api.hh.ru/areas'
    res = requests.get(url_areas)
    res.raise_for_status()
    res = json.loads(res.text)
    areas = {}
    if city:
        for area in res[0]['areas']:
            areas[area['name']] = area['id']
            if area['areas']:
                cur_area = area['areas']
                for cur_city in cur_area:
                    areas[cur_city['name']] = cur_city['id']
        for key, value in areas.items():
            if city.lower() == key.lower():
                city = areas[key]

    url = 'https://api.hh.ru/vacancies'
    params = {
        'text': f'{vacancy}',
        'area': city,
        'salary': str(salary),
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
            'salary': str(salary),
            'per_page': 100,
            'page': page
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        response = json.loads(response.text)
        vacancies += response['items']
        time.sleep(1)
    out_vacancies = []
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
        out_vacancy['key_skills'] = vac_skills
        description = response_vacancy['description']
        pattern = re.compile('<.*?>')
        description = re.sub(pattern, '', description)
        out_vacancy['description'] = description
        out_vacancy['url'] = response_vacancy['alternate_url']
        out_vacancies.append(out_vacancy)

    return {'ok': True, 'response': out_vacancies}


print(get_vacancies('разработчик', 'Оренбург', salary=500000))
