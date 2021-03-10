#!/bin/bash

if [[ -n "{FLASK_APP}" ]];
then python3.8 manage.py db upgrade;
fi

gunicorn -b 0.0.0.0 -w 3 "main:create_app()"