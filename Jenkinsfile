pipeline {

  agent {
    kubernetes {
      yamlFile 'jenkins-containers.yaml'
    }
  }

  environment {
        APP_NAME = "test-flask-webapp"
        GIT_REPO = "git@github.com:SyracuseUniversity/test-flask-webapp.git"
        RELEASE = "1.1"
        IMAGE_REPO = "harbor.ischool.syr.edu"
        IMAGE_GROUP = "ist_admins"
        IMAGE_NAME = "${IMAGE_REPO}" + "/" + "${IMAGE_GROUP}" + "/" + "${APP_NAME}"
        IMAGE_TAG = "${RELEASE}.${BUILD_NUMBER}"
        /* JENKINS_API_TOKEN = credentials("JENKINS_API_TOKEN") */

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
        MANIFEST_REPO = "git@github.com:SyracuseUniversity/ischool-k8s-test.git"
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
            sed -i "/$OLD_LINE/c\\ ${NEW_LINE}" `pwd`/${IMAGE_GROUP}/${APP_NAME}/deployment.yaml

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