FROM python:3.12-slim AS python-base
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
COPY vigor-exporter.py /app

EXPOSE 8000
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000", "vigor-exporter:app"]
