#! /usr/bin/env bash

# let the DB start
# sleep 5;

# initialize the database
touch /app/aitaws/prod.db
flask create_db
