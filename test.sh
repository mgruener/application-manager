#!/bin/bash
docker-compose down
docker-compose -f docker-compose.yml -f docker-compose.test.yml up --build