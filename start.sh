#!/bin/bash

if [[ -n "{FLASK_APP}" ]];
then flask db upgrade;
fi

gunicorn -b 0.0.0.0 -w 3 --keep-alive 90 "main:create_app()"