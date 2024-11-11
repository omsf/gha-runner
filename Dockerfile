FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
RUN mkdir app
COPY . /app
RUN pip install --no-cache-dir /app

CMD [ "python", "/app/src/gha_runner/" ]
