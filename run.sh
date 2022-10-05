#!/bin/bash

export FLASK_APP=phishsticks
export FLASK_ENV=development

create_cert () {
  openssl req -newkey rsa:4096 \
            -x509 \
            -sha256 \
            -nodes \
            -days 3650 \
            -out cert.pem \
            -keyout key.pem \
            -subj '/C=NA/ST=NA/L=NA/O=Phish/OU=Phisher/CN=phishsticks.internal'
}

CERT=cert.pem
KEY=key.pem
if [[ ! -f "$CERT" || ! -f "$KEY" ]]; then
    rm cert.pem > /dev/null 2>&1
    rm key.pem > /dev/null 2>&1
    create_cert
fi


flask run --host=127.0.0.1 --port=8888 --cert=cert.pem --key=key.pem