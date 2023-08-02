# start form a basic image with python 3.10
FROM python:3.10
# create a directory for the app
WORKDIR /app
# copy the requirements file to the app directory
COPY requirements.txt .
# install the requirements
RUN pip install -r requirements.txt
# install the gunicon for the flask app
RUN pip install gunicorn
# copy the template files to the app directory
COPY templates/ .
# copy the python files to the app directory
COPY get_cves.py .
COPY process_cves.py .
COPY app.py .
# expose the port 80
EXPOSE 80
# define the flaks app environment variable
ENV FLASK_APP=app.py
# define the flask app port
ENV FLASK_RUN_PORT=80
# start the flask app with gunicon
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
