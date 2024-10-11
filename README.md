# flask-mysql-example

This is a test flask web application that connect to a mysql backend. the purpose of this repository is to server as a template for creating porjects that use containers and the SU iSchool CI/CD pipelines.

## About the code
### Dependabot
Dependabot is a feature of Github that will automatically create pull-requests to update your projects dependencies. This will make sure that your code is using the most secure and up-to-date libraries. 

This feature does require manual intervention, having the user merge the pull-request with the main branch of the repository.

The Dependabot config is located in [.github/dependabot.yml](./.github/dependabot.yml).

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

The `CMD` command tells docker what command to use to run our container. It takes an array of strings containing the binary we want to run (in this case python), and it's arguments. In the example, we're telling the container to run python, and use the module gunicorn to serve app.py on port 5000:

```dockerfile
# open port and start app
EXPOSE 5000
CMD [ "python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "app:app" ]
```

### Jenkinsfile
The [Jenkinsfile](./Jenkinsfile) is an integral piece to the iSchool's CI/CD infrastructure. Once you have a repository with code configured to be run in a container, and a Jenkins file setup for your application, iSchool Technology Services administrators can setup your application in jenkins and Argo CD. Jenkins main purpose is to build a container image using your code, push it to an iSchool managed container registry, and update your kubernetes manifests for ArgoCD every time you push a change to your code in github. 

Basically, you push your code, and the system deploys it for you.

You'll want to copy the [Jenkinsfile](./Jenkinsfile) and [jenkins-containers.yaml](./jenkins-containers.yaml) to your repository.

> ![IMPORTANT]
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

### Application Code
#### dependencies

### Kubernetes Manifests
#### 
##