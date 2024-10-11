# use image hash to secure
FROM python:3.12-slim@sha256:15bad989b293be1dd5eb26a87ecacadaee1559f98e29f02bf6d00c8d86129f39

# create non-root user and use
RUN groupadd -g 999 python && \
    useradd -r -d /home/python -m -u 999 -g python python
USER 999
WORKDIR /usr/app

# install required libs
COPY requirements.txt .
RUN pip install -r requirements.txt

# move app over
COPY ./app .

# open port and start app
EXPOSE 5000
CMD [ "python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "app:app" ]