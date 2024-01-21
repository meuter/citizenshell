FROM ubuntu:18.04

RUN apt-get update && apt-get -y install --no-install-recommends \
    sudo \
    curl \
    git \
    python3 \
    python3-pip \
    python3-venv \
    python2.7 \
    python-setuptools \
    python-wheel \
    python-pip \
    virtualenv \
    build-essential \
    unzip
