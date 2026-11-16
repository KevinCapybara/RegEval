FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY regeval.py .
COPY core core
COPY tasks tasks
ENTRYPOINT ["python", "/app/regeval.py"]
