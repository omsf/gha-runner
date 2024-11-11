FROM python:3.10-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN uv sync --locked # This installs the dependencies
CMD ["uv", "run", "-m", "src/gha_runner"]
