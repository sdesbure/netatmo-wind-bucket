FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY netatmo-wind-bucket.py .

CMD ["python", "./netatmo-wind-bucket.py"]
