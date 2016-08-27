#!/usr/local/bin/python3
#
# Create VPC with public subnets in region in each AZ, plus correspond private subnets in each AZ for Elastic Beanstalk deployment
#
import boto3
import ipaddress
import itertools
import time
import webbrowser

region = 'us-west-2'
cidr_block = '10.1.0.0/16'
subnet_prefix_len = 24
vpc_name = 'shelde-test-vpc'
account_id = boto3.resource('iam').CurrentUser().arn.split(':')[4]

ec2client = boto3.client('ec2', region)

def list_availability_zone_names():
    response = ec2client.describe_availability_zones()
    zones = []
    for zone in response['AvailabilityZones']:
        zones.append(zone['ZoneName'])
    return zones

def create_vpc(cidr_block, vpc_name):
    response = ec2client.create_vpc(CidrBlock=cidr_block, InstanceTenancy='default')
    vpc_id = response['Vpc']['VpcId']
    response = ec2client.create_tags(Resources=[vpc_id], Tags=[{'Key': 'Name', 'Value': vpc_name}])
    return vpc_id

#
# We need one private subnet per public subnet per AZ - if there are 2 availability zones then we need four subnets
#
def create_subnets(vpc_name, vpc_id, cidr_block, availability_zones, subnet_prefix_len):
    num_subnets = len(availability_zones)
    subnets = ipaddress.ip_network(cidr_block).subnets(new_prefix=subnet_prefix_len)
    #
    # Public subnets
    #
    public_subnet_ids = []
    az_index = 0
    for subnet in itertools.islice(subnets, 0, num_subnets):
        zone_name = availability_zones[az_index]
        response = ec2client.create_subnet(VpcId=vpc_id, CidrBlock=str(subnet), AvailabilityZone=zone_name)
        subnet_id = response['Subnet']['SubnetId']
        response = ec2client.create_tags(Resources=[subnet_id], Tags=[{'Key': 'Name', 'Value': "%s-az%s" % (vpc_name, zone_name[-1:])}])
        public_subnet_ids.append(subnet_id)
        az_index += 1
    #
    # Private subnets
    #
    private_subnet_ids = []
    az_index = 0
    for subnet in itertools.islice(subnets, num_subnets, num_subnets):
        response = ec2client.create_subnet(VpcId=vpc_id, CidrBlock=str(subnet), AvailabilityZone=availability_zones[az_index])
        subnet_id = response['Subnet']['SubnetId']
        private_subnet_ids.append(subnet_id)
        response = ec2client.create_tags(Resources=[subnet_id], Tags=[{'Key': 'Name', 'Value': "%s-az%s-internal" % (vpc_name, zone_name[-1:])}])
        az_index += 1

    return public_subnet_ids, private_subnet_ids

#
# Do VPC creation
#
availability_zone_names = list_availability_zone_names()
vpc_id = create_vpc(cidr_block=cidr_block, vpc_name=vpc_name)
public_subnets, private_subnets = create_subnets(vpc_name=vpc_name, vpc_id=vpc_id, cidr_block=cidr_block, availability_zones=availability_zone_names, subnet_prefix_len=subnet_prefix_len)

exit(0)