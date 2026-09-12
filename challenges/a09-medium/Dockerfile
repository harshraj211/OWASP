FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

ENV LAB_PORT=6026
EXPOSE 6026

CMD ["python3", "app.py"]
