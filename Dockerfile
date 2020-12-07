FROM python:3.7

LABEL description "Renderable desktop client."
LABEL version "1.0.0"
LABEL maintainer "Danilo Peixoto <danilo@therenderable.com>"

WORKDIR /usr/src/renderable-catalyst/
COPY . .

RUN pip3 install --upgrade pip
RUN python3 setup.py install

CMD ["renderable-catalyst"]
