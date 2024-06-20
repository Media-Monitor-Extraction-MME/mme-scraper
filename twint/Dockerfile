FROM docker.io/python:3.12-slim as base

RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential wget curl python-dev-is-python3

# RUN mkdir -p /usr/src/python && \
#     cd /usr/src/python  && \
#     wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz && \
#     tar xzf Python-3.12.0.tgz && \
#     cd Python-3.12.0 && \
#     ./configure && \
#     make && \
#     make install

RUN pip install --upgrade pip setuptools

RUN pip install -U stweet


CMD /bin/bash -c "echo 'Hello World'; sleep infinity"