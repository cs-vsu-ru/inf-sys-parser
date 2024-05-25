FROM python:3.11.3

ARG GITHUB_REPO
LABEL org.opencontainers.image.source=https://github.com/${GITHUB_REPO}

WORKDIR /api

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=api.settings

COPY /requirements.txt ./requirements.txt

RUN pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install -r requirements.txt

COPY . .

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn api.wsgi -c gunicorn/config.py && python manage.py runserver" ]

#ENTRYPOINT python manage.py migrate && \
#    python manage.py collectstatic --noinput && \
#    gunicorn api.wsgi -c gunicorn/config.py