#!/bin/bash
from ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        tzdata build-essential libpq-dev libssl-dev libffi-dev python3-pip python3.8-dev cargo  \
        libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev postgresql postgresql-contrib \
    && rm -rf /var/lib/apt/lists/*

# RUN apt-get install autoconf libtool pkg-config python-opengl python-imaging python-pyrex python-pyside.qtopengl idle-python2.7  libqtgui4 libqtcore4 libqt4-xml libqt4-test libqt4-script libqt4-network libqt4-dbus  libgle3  -y
COPY . /app
WORKDIR app
RUN pip3 install -r requirements.txt

# libxml2-dev libxslt1-dev \ 
#         libldap2-dev libsasl2-dev

