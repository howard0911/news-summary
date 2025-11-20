FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
ENV FLASK_DEBUG=False

CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} backend.app:app"]

