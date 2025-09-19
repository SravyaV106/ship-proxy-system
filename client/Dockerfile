# ship/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY client.py /app/

EXPOSE 8080

CMD ["python", "client.py", "--offshore-host=OFFSHORE_HOST", "--offshore-port=9999"]
