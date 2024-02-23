FROM python:3.10.13

WORKDIR /app

COPY --chown=1000:1000 requirements.txt .

RUN pip install --no-cache -r requirements.txt

COPY --chown=1000:1000 . .