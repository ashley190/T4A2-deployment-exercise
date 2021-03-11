#!/bin/bash

if [[ -n "{FLASK_APP}" ]];
then flask db upgrade;
fi

gunicorn -b 0.0.0.0:8000 -w 3 "main:create_app()"