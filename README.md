# flask-mysql-example

This is a test flask web application that connect to a mysql backend. the purpose of this repository is to serve as a template for creating projects that use containers and the SU iSchool CI/CD pipelines.

> [!NOTE]
> Some steps will require the intervention of Technology Services Administrators.

## About the code
### Dependabot
Dependabot is a feature of Github that will automatically create pull-requests to update your projects dependencies. This will make sure that your code is using the most secure and up-to-date libraries. 

This feature does require manual intervention, having the repository maintainer (usually the person who creates the repository) merge the pull-request with the main branch of the repository.

The Dependabot config is located in [.github/dependabot.yml](./.github/dependabot.yml). It is configured to scan the `requirements.txt` for new pip packages and the `Dockerfile` for a new base image.

### Dockerfile
The Dockerfile tells docker how to package your application into a container. We will be using [this Dockerfile](./Dockerfile) in our examples. To learn more about Dockerfiles and their syntax, you can read more [here](https://docs.docker.com/reference/dockerfile/).

#### The base image
This is the base image our container starts from. For our application, we will be using the `python:3.x-slim` image. This means that we pull down an image from [Docker Hub](https://hub.docker.com/) that carries the binaries necessary to run a python application. Our line will look something like this in the file:

```dockerfile
# base image to use for container
FROM python:3.12-slim
```

#### Setting the runtime user
By default, docker will run a container as the root user. This is not a secure practice since this can allow attackers to breakout of a container image much easier. To help prevent a user from breaking out of our container, we create a non-privileged account & group named `python` in the container. You can do this with the following lines:

```dockerfile
# create non-privileged user to use
RUN groupadd -g 999 python && \
    useradd -r -d /home/python -m -u 999 -g python python
USER 999
```

#### Setting the working dir
Setting the working directory tells docker which directory you want your code to live and run from. We will set our working directory to `/usr/app`:

```dockerfile
# set the working directory
WORKDIR /usr/app
```

#### Installing dependencies
Our application most likely has code dependencies that don't come pre-installed in the container. We can use the `RUN` command to run some commands to install our application dependencies. In this example I will be using pip to install our dependecies. We can declare our dependencies in a `requirements.txt` file (you can learn more about this [here](#dependencies)), and copy it into the container. After that, we'll install our dependecies:

```dockerfile
# install required dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
```

#### Copy Application Code
This uses the `COPY` function to take our application code, and copy it into the container's working dirctory , `/usr/app`:

```dockerfile
# Copy application code into container
COPY ./app .
```

#### Run application
The last few lines of our Dockerfile help to run our application within the container. The `EXPOSE` function tells docker to open up port 5000 on the container for our application, since flask defaults to listening on port 5000.

The `CMD` command tells docker what command to use to run our container. It takes an array of strings containing the binary we want to run (in this case python), and its arguments. In the example, we're telling the container to run python, and use the module gunicorn to serve app.py on port 5000:

```dockerfile
# open port and start app
EXPOSE 5000
CMD [ "python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "app:app" ]
```

### Jenkinsfile
The [Jenkinsfile](./Jenkinsfile) is an integral piece to the iSchool's CI/CD infrastructure. Once you have a repository with code configured to be run in a container, and a Jenkins file setup for your application, iSchool Technology Services administrators can setup your application in jenkins and Argo CD. Jenkins main purpose is to build a container image using your code, push it to an iSchool managed container registry, and update your kubernetes manifests for ArgoCD every time you push a change to your code in github. 

Basically, you push your code, and the system deploys it for you.

You'll want to copy the [Jenkinsfile](./Jenkinsfile) and [jenkins-containers.yaml](./jenkins-containers.yaml) to your repository.

> [!IMPORTANT]
> If any of the following steps seem overwhelming or confusing, please reach out to the iSchool Technology Services team for assistance.

#### Environment

```jenkinsfile
...
  environment {
        APP_NAME = "flask-mysql-example"
        GIT_REPO = "git@github.com:SyracuseUniversity/flask-mysql-example.git"
        RELEASE = "1.0"
        IMAGE_REPO = "harbor.ischool.syr.edu"
        IMAGE_GROUP = "examples"
        IMAGE_NAME = "${IMAGE_REPO}" + "/" + "${IMAGE_GROUP}" + "/" + "${APP_NAME}"
        IMAGE_TAG = "${RELEASE}.${BUILD_NUMBER}"
  }
...
```
Change the following parameters to fit your application:
- `APP_NAME` will be the name for your application. you can make this whatever you want, as long as it only contains letters, numbers, and dashes ("-"). It must also be unique to your app. example: cool-app-2
- `GIT_REPO` will be the repository your code and this Jenkinsfile will live. 
- `RELEASE` is the version of your application. Jenkins will append a build number to this to use for versioning in the CI/CD system.
- `IMAGE_GROUP` will be the project group name you receive from the iSchool Tech Services admins.

#### Update k8s deployment manifest
```jenkinsfile
...
    stage('update k8s deployment manifest') {
      environment {
        MANIFEST_REPO = "git@github.com:SyracuseUniversity/flask-mysql-manifests-example.git"
        DEPLOYMENT_FILE = "app_deployment.yaml"
      }
...
```
Change the following parameters to fit your application:
- `MANIFEST_REPO` is the github repository where your kubernetes manifests will live.
- `DEPLOYMENT_FILE` is the file that will carry the deployment manifest for your application.

#### Update [jenkins-containers.yaml](./jenkins-containers.yaml) manifest
When setting up your application to use the iSchool's CI/CD pipeline, Technology Services admins will give you two values with the names `CODE_REPO_SECRET_NAME` and `MANIFEST_REPO_SECRET_NAME`. You will replace these names ('<' and '>' included) with the values provided to you.

```yaml
...
  volumes:
  - name: jenkins-docker-cfg
    projected:
      sources:
      - secret:
          name: <CODE_REPO_SECRET_NAME>
          items:
            - key: .dockerconfigjson
              path: config.json
  - name: git-ssh-key
    secret:
      secretName: <MANIFEST_REPO_SECRET_NAME>
```

### Application Code
#### Dependencies
Dependencies are stored in a [requirements.txt](./requirements.txt) file and installed using pip. Each line is a package that can be installed using pip. You can either just state the package name (i.e. "Flask"), or target a specific version of the package by appending "==" and specifying the version you'd like installed (i.e. "Flask==3.0.3").

```
Flask==3.0.3
gunicorn==23.0.0
Flask-SQLAlchemy==3.1.1
PyMySQL==1.1.1
```

#### Environment Variables
In [app/settings.py](./app/settings.py), we import the `environ` module from the built-in package, `os`. This allows us to read the values of environment variables that have been configured in the OS runtime. This is particularly useful in containerized applications, since it allows you to setup application configuration without the need for a configuration file.

```python
from os import environ, urandom
```

From here we assign environment variables to a static variable in python. with the `.get()` function, we are able to query for an environment variable by name. If the the environment variable does not exist, then the get function will take the optional second argument and use that as the default value. In this instance, if `APP_NAME` does not exist, it will be assigned the value "flask-mysql-example".

```python
# App settings
APP_NAME      = environ.get("APP_NAME", "flask-mysql-example")
```

In [app/app.py](./app/app.py), We import the file where we assigned our environment variables to python variables, and use the variables in our application logic:

```python
...
from settings import *
...
def debug_inputs():
    # print app version
    logger.info(f"{APP_NAME} {APP_VERSION}")

    # print environment variables
    logger.debug("Environment Variables")
    logger.debug(f"APP_NAME:        {APP_NAME}")
...
```

#### Logging
In containers, logging is usually written to `STD::OUT`. from here the container runtime environment will log it to a file. By default, most logging libraries want to log to a file. This application takes the standard logging library provided by python, and configures it write logs to `STD::OUT`. We can see an example of this in [app/app.py](./app/app.py):

```python
...
import logging
...

# create logger
logger = logging.getLogger(__name__)

# configure logger to output to stdout
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
...
```

Next, we use an environment variable to determine the level of logging we'd like to output. In [app/settings.py](./app/settings.py), we assign the `LOGGING_LEVEL` environment variable to a similar named python variable, and give it a default value of "INFO":

```python
...
LOGGING_LEVEL = environ.get("LOGGING_LEVEL","INFO")
...
```

Now, back in [app/app.py](./app/app.py), we use the environment variable to configure the logging level:

```python
...
# set log level
match LOGGING_LEVEL:
    case "DEBUG":
        logger.setLevel(logging.DEBUG)
    case "WARN":
        logger.setLevel(logging.WARN)
    case "ERROR":
        logger.setLevel(logging.ERROR)
    case _:
        logger.setLevel(logging.INFO)
...
```

Once this is configured, we can now log different levels of output:

```python
...
def debug_inputs():
    # print app version
    logger.info(f"{APP_NAME} {APP_VERSION}")

    # print environment variables
    logger.debug("Environment Variables")
    logger.debug(f"APP_NAME:        {APP_NAME}")
    logger.debug(f"APP_VERSION:     {APP_VERSION}")
    logger.debug(f"LOGGING_LEVEL:   {LOGGING_LEVEL}")
    logger.debug(f"APP_SECRET:      [redacted]")
    logger.debug(f"DB_HOST:         {DB_HOST}")
    logger.debug(f"DB_PORT:         {DB_PORT}")
    logger.debug(f"DB_NAME:         {DB_NAME}")
    logger.debug(f"DB_USER:         {DB_USER}")
    logger.debug(f"DB_PASS:         [redacted]")
...

@app.route('/add', methods=['POST'])
def add_entry():
    name = request.form.get('name',None)
    logger.info(f"Adding {name} to guestbook.")
...
```

Since we've configured logging in our main function, [app/app.py](./app/app.py), We don't have to reconfiure it in every file in our application. Just declare the logger variable. We can see this in [app/database.py](./app/database.py):

```python
...
import logging

# create logger
logger = logging.getLogger(__name__)
...

    def __init__(self, name):
        logger.debug(f"db object name: {name}")
...
```

#### Versioning
In our application, we've set up [app/version.txt](./app/version.txt) to hold the current version of our application. This allows us to determine the running version when deployed, and further helps with debugging.
If you notice in [Jenkinsfile](./Jenkinsfile), We write the IMAGE_TAG variable to this file before building our application's container:

```
...
    stage('Build & Push with Kaniko') {
      steps {
        container(name: 'kaniko', shell: '/busybox/sh') {
          sh '''#!/busybox/sh
            # push build number to app
            echo ${IMAGE_TAG} > `pwd`/app/version.txt
...
```

From here, we read the version from the `version.txt` file in [app/settings.py](./app/settings.py) and assign it to the variable `APP_VERSION`.

```python
...
from pathlib import Path
...

APP_VERISON   = Path('version.txt').read_text().replace('\n','')
...
```

From here we can output the version of our application to either our logs or output it on our web application. In our instance, we output it using the logs in [app/app.py](./app/app.py):

```python
...
from settings import *
...

def debug_inputs():
    # print app version
    logger.info(f"{APP_NAME} {APP_VERSION}")
...

if __name__ == '__main__':
    debug_inputs()
    app.run()
```

### Kubernetes Manifests
The kubernetes manifests for this application can be found [here](https://github.com/SyracuseUniversity/flask-mysql-manifests-example.git)

We keep the manifests in a seperate repository for ArgoCD to read from.