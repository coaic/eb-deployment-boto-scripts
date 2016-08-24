#!/usr/local/bin/python3

import boto3

region = 'us-west-2'
application_name = 'shelde01'
application_description = 'Test application for Shelde demo'
environment_name = application_name + '-' + 'blue'
environment_description = 'shelde01 blue environment'
template_name = 'blue_v1'
solution_stack = '64bit Amazon Linux 2016.03 v2.1.3 running Tomcat 8 Java 8'
template_description = 'shelde01 blue environment'
option_settings = [
    {
        "Namespace": "aws:autoscaling:launchconfiguration",
        "OptionName": "IamInstanceProfile",
        "Value": "aws-elasticbeanstalk-ec2-role"
    # },
    # {
    #     'ResourceName': 'string',
    #     'Namespace': 'string',
    #     'OptionName': 'string',
    #     'Value': 'string'
    }
]
client = boto3.client('elasticbeanstalk', region)

response = client.check_dns_availability(CNAMEPrefix=environment_name)
print("*** response.Available: %r, response.FullyQualifiedCNAME: %r" % (response['Available'], response['FullyQualifiedCNAME']))

# response = client.list_available_solution_stacks()
# print("*** Available solution stacks: ", response['SolutionStacks'])
# for stack in response['SolutionStacks']:
#     print(">>>> ", stack)

response = client.describe_applications(ApplicationNames=[application_name])
# print(response['Applications'][0]['ApplicationName'])

if not response['Applications'] or response['Applications'][0]['ApplicationName'] != application_name:
    response = client.create_application(ApplicationName=application_name, Description=application_description)
    print(response)

response = client.describe_applications(ApplicationNames=[application_name])

if not template_name in response['Applications'][0]['ConfigurationTemplates']:
    response = client.create_configuration_template(
        ApplicationName=application_name,
        TemplateName=template_name,
        SolutionStackName=solution_stack,
        Description=template_description,
        OptionSettings=option_settings
    )
    print(response)

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