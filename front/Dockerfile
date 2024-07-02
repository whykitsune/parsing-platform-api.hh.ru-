FROM python:3.10

RUN mkdir /parser_front

WORKDIR /parser_front

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD gunicorn front_main:front_app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000