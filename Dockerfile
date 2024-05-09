FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir .

CMD [ "python", "src/gha_runner/" ]
