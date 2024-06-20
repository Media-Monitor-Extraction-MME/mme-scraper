FROM docker.io/python:3.12-slim as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

FROM base AS runtime

RUN useradd --create-home appuser
WORKDIR /home/appuser

RUN pip install pipenv
RUN pip install playwright
RUN apt-get update && apt-get install -y --no-install-recommends gcc cron

COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy
RUN playwright install
RUN playwright install-deps

COPY cronms /etc/cron.d/cronms
RUN chmod 755 /etc/cron.d/cronms
RUN sed -i 's/\r//' /etc/cron.d/cronms
RUN crontab /etc/cron.d/cronms
RUN touch /var/log/cron.log
RUN ln -sf /dev/stdout /var/log/cron.log


RUN chmod 777 /var/log/cron.log
USER appuser

ARG VERSION=1.0.0

COPY . .
RUN touch logs.log
RUN chmod 777 logs.log

USER root
RUN chmod +x start_services.sh
ENTRYPOINT ["/home/appuser/start_services.sh"]