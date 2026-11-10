FROM gcc:13-bookworm

RUN apt-get update \
 && apt-get install -y --no-install-recommends time \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -u 1000 runner

USER 1000:1000
WORKDIR /work

CMD ["/bin/bash"]