FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends time \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -u 1000 runner

USER 1000:1000
WORKDIR /work

ENTRYPOINT ["python"]