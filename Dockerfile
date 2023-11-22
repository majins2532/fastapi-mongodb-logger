FROM digitalorganic/fastapi:3.10

RUN apt-get update && apt-get install -y --no-install-recommends wget vim && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY ./app /app/

VOLUME ["/var/log/fastapi"]

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "trace"]
