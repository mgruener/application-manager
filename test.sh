#!/bin/bash
export EJSON_KEYDIR="${HOME}/ejson/keys"
mkdir -p data
ejson decrypt -o data/appman_settings.json appman_settings.ejson
docker-compose down
docker-compose -f docker-compose.yml -f docker-compose.test.yml up --build