FROM python:3.6-alpine

RUN apk update && apk add --no-cache build-base
WORKDIR /app

# python reqs
COPY ./requirements.txt .
COPY ./requirements-test.txt .
RUN pip install --no-cache-dir \
    -r requirements.txt \
    -r requirements-test.txt

CMD [ "python" ]