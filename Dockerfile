FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e .
COPY . /app
CMD ["python", "-m", "app.cli"]
