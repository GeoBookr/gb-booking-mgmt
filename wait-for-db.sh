#!/bin/bash
set -e

echo "Waiting for CockroachDB to be ready..."

python -c "
import socket, time
while True:
    try:
        socket.create_connection(('cockroachdb', 26257), timeout=2)
        print('CockroachDB is up!')
        break
    except:
        print('Waiting for CockroachDB')
        time.sleep(1)
"

echo "CockroachDB is up!"

# echo "Ensuring 'journey_db' exists..."
# cockroach sql --insecure --host=cockroachdb -e "CREATE DATABASE IF NOT EXISTS journey_db;"


# echo "Ensuring migrations are completed"
python db/init_db.py

echo "Starting the app..."
exec "$@"
