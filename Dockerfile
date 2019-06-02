FROM python:3-alpine

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="Netatmo Wind Bucket" \
      org.label-schema.description="Store wind data from netatmo into buckets" \
      org.label-schema.url="https://github.com/sdesbure/netatmo-wind-bucket" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/sdesbure/netatmo-wind-bucket" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY netatmo-wind-bucket.py .

CMD ["python", "./netatmo-wind-bucket.py"]
