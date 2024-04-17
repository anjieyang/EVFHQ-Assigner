FROM python:3.10-slim

RUN apt-get update && apt-get install -y libpq-dev gcc

WORKDIR /data1/EVFHQ/Assigner

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python3", "main.py"]