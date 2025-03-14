FROM python:3.11-slim

WORKDIR /app

RUN apt-get update
RUN apt-get install build-essential -y

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3000", "--workers", "4", "--reload"]