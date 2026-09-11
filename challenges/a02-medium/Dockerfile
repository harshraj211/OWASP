FROM python:3.11-slim

WORKDIR /app

RUN addgroup --system lab && adduser --system --ingroup lab lab

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=lab:lab . .

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER lab
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:5000/healthz', timeout=2)"

CMD ["python", "app.py"]
