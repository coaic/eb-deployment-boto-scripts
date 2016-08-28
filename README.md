# eb-deployment-boto-scripts
#### Suite of orchestration scripts to create VPC, EFS File System, CloudFront Distribution and Elastic Beanstalk
##### Assumptions

The scripts make several assumptions about the AWS environment:

1.  Python3 is installed

2.  Assumes all scripts are in current directory.

3.  Assumes the region is us-west-2

4.  Assumes the .war file to be launched is in the same folder as the scripts and is named ROOT.war

5.  Assumes an email address for Simple Notification Service notifications: rcoaic at gmail dot com

6.  The AWS CLI must be installed. Refer to: http://docs.aws.amazon.com/cli/latest/userguide/installing.html

7.  Assumes aws configure set preview.cloudfront true command has been run so that CloudFront can be configured.

8.  The aws configure command must be run to store/configure an API key/secret that can be accessed via commands.

9.  No API keys or account credentials are stored in the scripts or repository.

10.  The development environment is currently Mac OS command line.

11. Various packages not provided via Mac OS have been installed with Homebrew. Refer to http://brew.sh

12. There is a reliance on AWS Elastic Beanstalk to create an initial bucket to maintain configuration data needed by
    the service in the region being used.

13. Assumes an EC2 key pair exists for the region, assumes shelde-test-us-west-2.

14. Assumes default roles have been created by Elastic Beanstalk named: aws-elasticbeanstalk-ec2-role and aws-elasticbeanstalk-service-role
    -- this is a one time requirement, roles are not region specific.
    -- aws-elasticbeanstalk-ec2-role should have the attached policies { AWSElasticBeanstalkWebTier, CloudWatchLogsFullAccess,
                                                                         AWSElasticBeanstalkMulticontainerDocker, AWSElasticBeanstalkWorkerTier }
    -- aws-elasticbeanstalk-service-role should have attached policies { AWSElasticBeanstalkEnhancedHealth, AWSElasticBeanstalkService }

15. The EC2s launched by Elastic Beanstalk have public IPs assigned -- public internet connectivity is required for the EC2s to access
    Elastic Beanstalk API end points.

16. An alternative would be to modify the VPC creation script to create a NAT Service in a public subnet to allow instances with only
    private IPs to have AWS API access to the NAT service.

17. If you want to rerun ./create_beanstalk_with_eb_api.py from console, please ensure you terminate the environment followed by deleting the
    application in the AWS Console.

18. Prior to deployment the .war file is unpacked to ./war, the .ebextensions folder in the root of the .war is removed and seeded with configured
    .ebextensions folder to allow configuring launched Ec2s with access to the Elastic File System File at /efs on the EC2. The static assets are
    moved to a folder ./assets to be coppied to an S3 bucket prefix.

##### Running the scripts

You can run the scripts in the correct order by running the script **run_environment.sh**. Alternatively your can run the scripts in more or less the following order, 
depending on what you want to achieve:

* **create_eb_vpc_with_ec2_api.py** - Creates the a VPC with public and private subnets, distributed across all availability zones in the region.

* **create_beanstalk_with_eb_eb_api.py** - Creates a Java beanstalk in the previously created VPC in with the webworker EC2s deployed behind an Elastic
Load Balancer in the public subnets. Each EC2 on launch is automatically connected to an Elastic File System file store mounted at **/efs**.
The beanstalk is deployed with a default Java application which can be replaced by running **deploy_application_with_eb_api.py**.

* **deploy_application_with_eb_api.py** - Deploys a *.war* file *ROOT.war* to the running beanstalk. As part of the script operations, the .war is unpacked, 
*.ebextensions* removed, and replaced with an updated .ebextensions that includes functions to enable *CloudWatch Logs* and *Elastic File System*.

* **create_cloud_front_distribution.sh** - Creates an S3 bucket, use *aws s3 sync* to sync static content to a bucket prefix */blue* and deploys a *CloudFront* distribution
that use the S3 bucket as an origin at the */blue* prefix.