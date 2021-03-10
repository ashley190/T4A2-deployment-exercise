FROM ubuntu:latest
RUN apt-get update
RUN apt-get install python3.8 python3-pip gunicorn -y
WORKDIR /code
COPY src .
RUN pip3 install -r requirements.txt
RUN if [[ -n "${FLASK_APP}" ]]; then python3.8 manage.py db upgrade; fi
CMD [ "gunicorn", "-b", "0.0.0.0", "-w", "3", "main:create_app()" ]