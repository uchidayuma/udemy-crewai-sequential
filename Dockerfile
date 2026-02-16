FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/        ./app/
COPY frontend/   ./frontend/
COPY data_import/ ./data_import/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
