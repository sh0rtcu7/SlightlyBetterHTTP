FROM python:3.13.0b2-slim-bookworm
WORKDIR /app/
COPY *.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 80
ENTRYPOINT [ "python", "app.py" ]