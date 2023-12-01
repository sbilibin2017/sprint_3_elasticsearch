#!/bin/bash

echo "Waiting for postgres..."
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 10
    done

    echo "PostgreSQL started"
fi

python3 main.py

exec "$@"