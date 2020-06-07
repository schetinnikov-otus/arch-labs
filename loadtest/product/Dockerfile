FROM python:3.8.3-alpine

ENV VIRTUAL_ENV "/venv"
RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

RUN apk add postgresql-dev
RUN apk add build-base

WORKDIR /usr/src/app
COPY ./requirements.txt /usr/src/app
RUN python -m pip install -r requirements.txt

COPY . /usr/src/app/
EXPOSE 8000

ENTRYPOINT ["python", "/usr/src/app/src/app.py"]
