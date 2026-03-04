FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

# Create venv and make it the active environment
RUN uv venv /venv
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"

# Install deps INTO the active venv
RUN uv sync --frozen --no-dev --active

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# More robust than relying on a uvicorn executable being on PATH
CMD ["python", "-m", "uvicorn", "renovaite.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
