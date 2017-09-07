## Domain Scan Orchestration

This tool is called domain scan orchestration, it automates the process of running [domain-scan](https://github.com/18F/domain-scan) on [cloud.gov](https://cloud.gov/). 

## About this project

This project assumes you are using Python3.  This solution is untested for Python2, so use at your own risk!

## Setup

To get this tool working you'll need to first login to cloud.gov - documentation for that can be found [here](https://cloud.gov/docs/getting-started/setup/).  Once you are logged into cloud.gov, you can deploy the app!

The first thing you'll need to do is create an s3 service called dotgov_subdomains.  You'll need this for when you deploy to cloud.gov.

To create an s3 service do the following:

`cf create-service s3 basic-public dotgov_subdomains`

The cloud.gov recommends also doing the following 2 commands:

`cf bind-service <APP_NAME> <SERVICE_INSTANCE_NAME>`

`cf restage <APP_NAME>`

However, you should need to do this because the services is being bound at deploy time.

To deploy - from the root directory of the project do the following:

`cd scheduler`

`python deployer.py #pushes scheduler to cloud.gov` 

After that you should have 
