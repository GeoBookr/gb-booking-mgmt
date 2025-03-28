FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY main.py .

EXPOSE 7444

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7444", "--reload"]
