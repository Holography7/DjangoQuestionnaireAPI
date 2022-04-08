###########
# BUILDER #
###########

FROM python:3.8-alpine

WORKDIR /usr/src/questionnaire

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache gcc musl-dev python3-dev
RUN pip install ruamel.yaml.clib

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/questionnaire/entrypoint.sh
RUN chmod +x /usr/src/questionnaire/entrypoint.sh

COPY . .

ENTRYPOINT ["/usr/src/questionnaire/entrypoint.sh"]
