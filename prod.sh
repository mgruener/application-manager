#!/bin/bash
if [ "${1}" = "master" ]; then
  export STAGE=""
else
  export STAGE="${1}."
fi
docker-compose down
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build