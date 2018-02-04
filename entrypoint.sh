#!/bin/bash

sleep 30

cd $APPLICATION_ROOT\app
export FLASK_DEBUG=1
FLASK_APP=app.py flask run --host=0.0.0.0 --port=5000
