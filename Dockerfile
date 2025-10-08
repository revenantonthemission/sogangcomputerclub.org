FROM python:3.13
WORKDIR /code
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY ./pyproject.toml ./uv.lock ./README.md /code/
RUN uv sync --frozen --no-cache
COPY ./app /code/app
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]