FROM python:3.6-stretch

MAINTAINER cgebe

RUN apt-get update && \
    apt-get install -y cpanminus && \
    cpanm --force XML::Parser

COPY . /etc/rouge
WORKDIR /etc/rouge

RUN pip install -U git+https://github.com/pltrdy/pyrouge && \
    echo | python setup_rouge.py && \
    python setup.py install

ENV DATA_DIR /etc/rouge/data
VOLUME ["/etc/rouge/data"]

ENTRYPOINT ["/bin/bash"]
