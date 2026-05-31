FROM hivesolutions/python:latest

LABEL version="1.0"
LABEL maintainer="Hive Solutions <development@hive.pt>"

EXPOSE 8080

ENV LEVEL=INFO
ENV SERVER=netius
ENV SERVER_ENCODING=gzip
ENV HOST=0.0.0.0
ENV PORT=8080
ENV MONGOHQ_URL=mongodb://localhost
ENV PYTHONPATH=/src

ADD requirements.txt /
ADD extra.txt /
ADD src /src

RUN apk update && apk add libpng-dev libjpeg-turbo-dev libwebp-dev freetype-dev
RUN pip3 install -r /requirements.txt && pip3 install -r /extra.txt && pip3 install --upgrade netius

RUN groupadd --system --gid 10001 budy && \
    useradd --system --uid 10001 --gid budy --home-dir /src --shell /usr/sbin/nologin budy && \
    chown -R budy:budy /src
USER budy

CMD ["/usr/bin/python3", "/src/budy/main.py"]
