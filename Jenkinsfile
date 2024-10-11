pipeline {

  agent {
    kubernetes {
      yamlFile 'jenkins-containers.yaml'
    }
  }

  environment {
        APP_NAME = "flask-mysql-example"
        GIT_REPO = "git@github.com:SyracuseUniversity/flask-mysql-example.git"
        RELEASE = "1.0"
        IMAGE_REPO = "harbor.ischool.syr.edu"
        IMAGE_GROUP = "examples"
        IMAGE_NAME = "${IMAGE_REPO}" + "/" + "${IMAGE_GROUP}" + "/" + "${APP_NAME}"
        IMAGE_TAG = "${RELEASE}.${BUILD_NUMBER}"
    }

  stages {

    stage("Cleanup Workspace") {
      steps {
        cleanWs()
      }
    }

    stage("Checkout from SCM"){
            steps {
                git branch: 'main', credentialsId: "${APP_NAME}-key", url: "${GIT_REPO}"
            }

        }

    stage('Build & Push with Kaniko') {
      steps {
        container(name: 'kaniko', shell: '/busybox/sh') {
          sh '''#!/busybox/sh
            # push build number to app
            echo ${IMAGE_TAG} > `pwd`/app/version.txt

            # build container image and ship
            /kaniko/executor --dockerfile `pwd`/Dockerfile --context `pwd` --destination=${IMAGE_NAME}:${IMAGE_TAG} --destination=${IMAGE_NAME}:latest
          '''
        }
      }
    }

    stage("Cleanup Workspace Again") {
      steps {
        cleanWs()
      }
    }

    stage('update k8s deployment manifest') {
      environment {
        MANIFEST_REPO = "git@github.com:SyracuseUniversity/flask-mysql-manifests-example.git"
        DEPLOYMENT_FILE = "app_deployment.yaml"
      }
      steps {
        container(name: 'git', shell: '/bin/sh') {
          sh '''#!/bin/sh
            # set up ssh key and github hostkey
            mkdir ~/.ssh
            chmod 700 ~/.ssh
            cp /keys/id_rsa ~/.ssh/id_rsa
            chmod 600 ~/.ssh/id_rsa
            ssh-keyscan -H github.com >> ~/.ssh/known_hosts

            # clone repo
            git clone $MANIFEST_REPO `pwd`/manifests
            cd `pwd`/manifests

            # update build tag
            export OLD_LINE="^[[:space:]]*image: harbor.ischool.syr.edu"
            export NEW_LINE="       image: ${IMAGE_NAME}:${IMAGE_TAG}"
            sed -i "/$OLD_LINE/c\\ ${NEW_LINE}" `pwd`/${DEPLOYMENT_FILE}

            # push changes
            git config user.email "ischoolit@ot.syr.edu"
            git config user.name "iSchool Jenkins"
            git add .
            git commit -m "build(${APP_NAME}): updated container build tag to ${IMAGE_TAG}"
            git push origin main
          '''
        }
      }
    }

  }
}