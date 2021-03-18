# Introduction
This is an AWS deployment exercise using a Flask application developed for one of my Coder Academy assessments. Deployment was attempted using the following methods:-

## Manual deployment

This app was initially deployed manually using the following AWS architecture.
![manual deployment](docs/AAD_manual.png)

All components were set up on AWS manually such as:-

* Virtual Private Cloud - Public and Private subnets, internet gateway allowing the app to communicate externally with clients and external API.
* EC2 instances running the flask applications that communicates using with a database sitting in a private subnet using ORM.
* S3 bucket holding files that can be read/write through the flask application.
* Application Load Balancer to load balance two EC2 instances for availability and redundancy. The ALB has been configured to route all traffic through HTTPS for enhanced security.
* Route 53 for DNS resolution which allows for the ALB to be accessible via a domain name.


## ECR and ECS deployment