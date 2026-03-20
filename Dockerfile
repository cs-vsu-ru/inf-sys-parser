FROM python:3.11.3

ARG GITHUB_REPO
LABEL org.opencontainers.image.source=https://github.com/${GITHUB_REPO}

WORKDIR /api

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=api.settings

COPY requirements.txt ./requirements.txt

RUN python -m pip install --upgrade pip && \
    # Ensure setuptools/pkg_resources are installed in the final image.
    python -m pip install --no-cache-dir --force-reinstall "setuptools<82" && \
    python -m pip install --no-cache-dir -r requirements.txt

# Fail fast if image doesn't contain setuptools/pkg_resources.
RUN python -c "import pkg_resources; print('pkg_resources ok')"

COPY . .

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn api.wsgi -c gunicorn/config.py && python manage.py runserver" ]

#ENTRYPOINT python manage.py migrate && \
#    python manage.py collectstatic --noinput && \
#    gunicorn api.wsgi -c gunicorn/config.py