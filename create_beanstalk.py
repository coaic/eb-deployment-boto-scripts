#!/usr/local/bin/python3
#
import boto3

region = 'us-west-2'
vpc_id = 'vpc-425c7726'
webserver_subnets = "subnet-3e5f2948,subnet-b9aff1dd,subnet-9640f1ce"
instance_type = 't2.micro'
healthcheck_url ='/'
cool_down = str(60 * 6)
autoscale_max_instance = '4'
autoscale_min_instance = '1'
ssh_key_name = 'shelde-test-us-west-2'
ssh_restrictions = 'tcp,22,22,124.149.49.200/32'
instance_profile = 'aws-elasticbeanstalk-ec2-role'
service_role = 'aws-elasticbeanstalk-service-role'
instance_security_group = 'sg-63372a05'
#
#
#
application_name = 'shelde01'
application_description = 'Test application for Shelde demo'
environment_name = application_name + '-' + 'blue'
environment_description = 'shelde01 blue environment'
template_name = 'blue_v1'
solution_stack = '64bit Amazon Linux 2016.03 v2.2.0 running Tomcat 8 Java 8'
template_description = 'shelde01 blue environment'
option_settings = [
    {
        "OptionName": "IamInstanceProfile",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "Value": "aws-elasticbeanstalk-ec2-role"
    },
    {
        "OptionName": "VPCId",
        "Namespace": "aws:ec2:vpc",
        "Value": vpc_id
    },
    {
        "OptionName": "Subnets",
        "Namespace": "aws:ec2:vpc",
        "Value": webserver_subnets
    },
    {
        "OptionName": "ELBSubnets",
        "Namespace": "aws:ec2:vpc",
        "Value": webserver_subnets
    },
    {
        "OptionName": "AssociatePublicIpAddress",
        "ResourceName": "AWSEBAutoScalingLaunchConfiguration",
        "Namespace": "aws:ec2:vpc",
        "Value": "true"
    },
    {
        "OptionName": "ELBScheme",
        "Namespace": "aws:ec2:vpc",
        "Value": "public"
    },
    {
        "OptionName": "Availability Zones",
        "ResourceName": "AWSEBAutoScalingGroup",
        "Namespace": "aws:autoscaling:asg",
        "Value": "Any"
    },
    {
        "OptionName": "Cooldown",
        "ResourceName": "AWSEBAutoScalingGroup",
        "Namespace": "aws:autoscaling:asg",
        "Value": cool_down
    },
    {
        "OptionName": "MaxSize",
        "ResourceName": "AWSEBAutoScalingGroup",
        "Namespace": "aws:autoscaling:asg",
        "Value": autoscale_max_instance
    },
    {
        "OptionName": "MinSize",
        "ResourceName": "AWSEBAutoScalingGroup",
        "Namespace": "aws:autoscaling:asg",
        "Value": autoscale_min_instance
    },
    {
        "OptionName": "BlockDeviceMappings",
        "ResourceName": "AWSEBAutoScalingLaunchConfiguration",
        "Namespace": "aws:autoscaling:launchconfiguration"
    },
    {
        "OptionName": "EC2KeyName",
        "ResourceName": "AWSEBAutoScalingLaunchConfiguration",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "Value": ssh_key_name
    },
    {
        "OptionName": "IamInstanceProfile",
        "ResourceName": "AWSEBAutoScalingLaunchConfiguration",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "Value": instance_profile
    },
    {
        "OptionName": "ServiceRole",
        "Namespace": "aws:elasticbeanstalk:environment",
        "Value": service_role
    },
    {
        "OptionName": "SSHSourceRestriction",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "Value": ssh_restrictions
    },
    {
        "OptionName": "SecurityGroups",
        "ResourceName": "AWSEBAutoScalingLaunchConfiguration",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "Value": instance_security_group
    },
    {
        "OptionName": "JDBC_CONNECTION_STRING",
        "Namespace": "aws:elasticbeanstalk:application:environment",
        "Value": ""
    },
    {
        "OptionName": "DeploymentPolicy",
        "Namespace": "aws:elasticbeanstalk:command",
        "Value": "Rolling"
    },
    {
        "OptionName": "MaxBatchSize",
        "ResourceName": "AWSEBAutoScalingGroup",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate",
        "Value": "1"
    },
    {
        "OptionName": "MinInstancesInService",
        "ResourceName": "AWSEBAutoScalingGroup",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate",
        "Value": "1"
    },
    {
        "OptionName": "PauseTime",
        "ResourceName": "AWSEBAutoScalingGroup",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate"
    },
    {
        "OptionName": "RollingUpdateEnabled",
        "ResourceName": "AWSEBAutoScalingGroup",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate",
        "Value": "true"
    },
    {
        "OptionName": "RollingUpdateType",
        "ResourceName": "AWSEBAutoScalingGroup",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate",
        "Value": "Health"
    },
    {
        "OptionName": "Timeout",
        "ResourceName": "AWSEBAutoScalingGroup",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate",
        "Value": "PT30M"
    },
    {
        "OptionName": "HealthCheckSuccessThreshold",
        "Namespace": "aws:elasticbeanstalk:healthreporting:system",
        "Value": "Ok"
    },
    {
        "OptionName": "SystemType",
        "Namespace": "aws:elasticbeanstalk:healthreporting:system",
        "Value": "enhanced"
    },
    {
        "Namespace": "aws:autoscaling:launchconfiguration",
        "OptionName": "InstanceType",
        "Value": instance_type
    },
    {
        "OptionName": "Application Healthcheck URL",
        "Namespace": "aws:elasticbeanstalk:application",
        "Value": healthcheck_url
    },
    {
        "OptionName": "ConnectionDrainingEnabled",
        "ResourceName": "AWSEBLoadBalancer",
        "Namespace": "aws:elb:policies",
        "Value": "true"
    },
    # {
    #     'ResourceName': 'string',
    #     'Namespace': 'string',
    #     'OptionName': 'string',
    #     'Value': 'string'
    # }
]
client = boto3.client('elasticbeanstalk', region)

response = client.check_dns_availability(CNAMEPrefix=environment_name)
if not response['Available']:
    print("ERROR: Environment name: %s already in use." % environment_name)
    exit(1)

# response = client.list_available_solution_stacks()
# print("*** Available solution stacks: ", response['SolutionStacks'])
# for stack in response['SolutionStacks']:
#     print(">>>> ", stack)

response = client.describe_applications(ApplicationNames=[application_name])
# print(response['Applications'][0]['ApplicationName'])

if not response['Applications'] or response['Applications'][0]['ApplicationName'] != application_name:
    response = client.create_application(ApplicationName=application_name, Description=application_description)

response = client.describe_applications(ApplicationNames=[application_name])

if not template_name in response['Applications'][0]['ConfigurationTemplates']:
    response = client.create_configuration_template(
        ApplicationName=application_name,
        TemplateName=template_name,
        SolutionStackName=solution_stack,
        Description=template_description,
        OptionSettings=option_settings
    )

response = client.create_environment(
    ApplicationName=application_name,
    EnvironmentName=environment_name,
#    GroupName='string',
    Description=environment_description,
    CNAMEPrefix=environment_name,
    Tier={
        'Name': 'WebServer',
        'Type': 'Standard'
    },
    Tags=[
        {
            'Key': 'name',
            'Value': environment_name
        },
    ],
    # VersionLabel='string',
    TemplateName=template_name,
    SolutionStackName=solution_stack
    # OptionSettings=[
    #     {
    #         'ResourceName': 'string',
    #         'Namespace': 'string',
    #         'OptionName': 'string',
    #         'Value': 'string'
    #     },
    # ],
    # OptionsToRemove=[
    #     {
    #         'ResourceName': 'string',
    #         'Namespace': 'string',
    #         'OptionName': 'string'
    #     },
    # ]
)
print(response)