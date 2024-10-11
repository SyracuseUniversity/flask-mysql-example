# base image to use for container
FROM python:3.12-slim

# create non-privileged user to use
RUN groupadd -g 999 python && \
    useradd -r -d /home/python -m -u 999 -g python python
USER 999

# set the working directory
WORKDIR /usr/app

# install required dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code into container
COPY ./app .

# open port and start app
EXPOSE 5000
CMD [ "python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "app:app" ]