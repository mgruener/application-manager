FROM alpine:3.6
EXPOSE 3031
VOLUME /usr/src/app/public
WORKDIR /usr/src/app
RUN apk add --no-cache \
        uwsgi \
        uwsgi-python3 \
        python3 \
        py3-lxml \
        py3-crypto
COPY . .
RUN rm -rf public/*
RUN pip3 install --no-cache-dir -r requirements.txt
CMD [ "uwsgi", "--socket", "0.0.0.0:3031", \
               "--plugins", "python3", \
               "--protocol", "http", \
               "--module", "application_manager:create_app()" ]

