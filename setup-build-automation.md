# setup-build-automation
used to store Jenkins file for building test-flask-webapp

## Setup
### Create and store SSH key
#### Create and output keys
```bash
# create SSH keypair
ssh-keygen -t rsa -b 4096 -f `pwd`/build-test-flask-webapp-key -C "Read-only key for pulling build repo." -q

# output public key
cat `pwd`/build-test-flask-webapp-key.pub

# output private key
cat `pwd`/build-test-flask-webapp-key
```

#### Add public key to github
1. In this repo, go to "Settings" > "Deploy keys" and click on "Add deploy key"
    - **Title**: Jenkins Key
    - **Key**: *Output of build-test-flask-webapp-key.pub*
2. Click *Add Key*.

#### Add private key to jenkins
1. In Jenkins, navigate to “Manage Jenkins” > “Credentials” > "System" > "Global Credentials"
2. Click on “Add Credentials” and choose “SSH Username with private key.”
    - **ID**: build-test-flask-webapp-key
    - **Username**: git
    - **Private Key**: *Select "Enter Directly" then click "Add", pasting the output of private key.*
3. Click "Create".

### Create kubernetes secret for pushing container image
```bash
kubectl create secret docker-registry build-test-flask-webapp \
-n devops-tools \
--docker-server=harbor.ischool.syr.edu \
--docker-username='robot$ist_admins+jenkins_push' \
--docker-password=<REDACTED>
```