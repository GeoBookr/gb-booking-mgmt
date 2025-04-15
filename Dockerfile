FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN echo "Hello"

COPY . .

EXPOSE 7444

COPY wait-for-db.sh /wait-for-db.sh

ENTRYPOINT ["/wait-for-db.sh"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7444", "--reload"]
