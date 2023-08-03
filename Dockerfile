# start form a basic image with python 3.10
FROM python:3.10
# create a directory for the app
WORKDIR /app
# copy the requirements file to the app directory
COPY requirements.txt .
# install the requirements
RUN pip install --no-cache-dir -r requirements.txt
# install the gunicon for the flask app
RUN pip install gunicorn
# copy the template files to the app directory
COPY templates ./templates
# copy the python files to the app directory
COPY get_cves.py .
COPY process_cves.py .
COPY app.py .
COPY software.json .
# expose the port 80
# start only one instance of the app with gunicorn on port 80
EXPOSE 80
# start the app
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
