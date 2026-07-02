FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# --preload loads the app (and runs db.create_all) once in the master
# process before forking workers, avoiding a schema-creation race.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--preload", "wsgi:app"]
