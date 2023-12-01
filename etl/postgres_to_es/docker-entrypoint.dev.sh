#!/bin/bash

if [ "$ES" = "true" ]
then
    echo "Waiting for elasticsearch..."

    while ! nc -z $ES_HOST $ES_PORT; do
      sleep 1
    done

    echo "Elasticsearch started"
fi
python3 main.py