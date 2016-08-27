#!/usr/local/bin/python3
#
# Create VPC with public subnets in region in each AZ, plus correspond private subnets in each AZ for Elastic Beanstalk deployment
#
import boto3
import ipaddress
import itertools
import time

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
    ec2client.get_waiter('vpc_available').wait(VpcIds=[vpc_id])
    response = ec2client.create_tags(Resources=[vpc_id], Tags=[{'Key': 'Name', 'Value': vpc_name}])
    response = ec2client.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
    response = ec2client.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})
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
    for subnet in itertools.islice(subnets, num_subnets):
        zone_name = availability_zones[az_index]
        response = ec2client.create_subnet(VpcId=vpc_id, CidrBlock=str(subnet), AvailabilityZone=zone_name)
        subnet_id = response['Subnet']['SubnetId']
        ec2client.get_waiter('subnet_available').wait(SubnetIds=[subnet_id])
        response = ec2client.create_tags(Resources=[subnet_id], Tags=[{'Key': 'Name', 'Value': "%s-az%s" % (vpc_name, zone_name[-1:])}])
        public_subnet_ids.append(subnet_id)
        az_index += 1

    #
    # Private subnets
    #
    private_subnet_ids = []
    az_index = 0
    for subnet in itertools.islice(subnets, num_subnets):
        zone_name = availability_zones[az_index]
        response = ec2client.create_subnet(VpcId=vpc_id, CidrBlock=str(subnet), AvailabilityZone=availability_zones[az_index])
        subnet_id = response['Subnet']['SubnetId']
        private_subnet_ids.append(subnet_id)
        ec2client.get_waiter('subnet_available').wait(SubnetIds=[subnet_id])
        response = ec2client.create_tags(Resources=[subnet_id], Tags=[{'Key': 'Name', 'Value': "%s-az%s-internal" % (vpc_name, zone_name[-1:])}])
        az_index += 1

    return public_subnet_ids, private_subnet_ids

#
# Create an Internet Gateway for the public subnets
#
def create_igw(vpc_name, vpc_id):
    response = ec2client.create_internet_gateway()
    internet_gateway_id = response['InternetGateway']['InternetGatewayId']
    response = ec2client.create_tags(Resources=[internet_gateway_id], Tags=[{'Key': 'Name', 'Value': "%s-gateway" % (vpc_name)}])
    response = ec2client.attach_internet_gateway(InternetGatewayId=internet_gateway_id, VpcId=vpc_id)
    return internet_gateway_id

#
# Create route tables for public subnets and seperately for private subnets
#
def create_route_tables(vpc_name, vpc_id, igw_id, public_subnets, private_subnets):
    #
    # Create public route table
    #
    response = ec2client.create_route_table(VpcId=vpc_id)
    public_route_table_id = response['RouteTable']['RouteTableId']
    response = ec2client.create_tags(Resources=[public_route_table_id], Tags=[{'Key': 'Name', 'Value': "%s-public-route-table" % (vpc_name)}])
    #
    # Associate public subnets and internet gateway route
    #
    for subnet in public_subnets:
        response = ec2client.associate_route_table(SubnetId=subnet, RouteTableId=public_route_table_id)

    response = ec2client.create_route(RouteTableId=public_route_table_id, DestinationCidrBlock='0.0.0.0/0', GatewayId=igw_id)
    if not response['Return']:
        print("ERROR: Failed to add public subnet IGW route")
        exit(1)
    #
    # Create private route table
    #
    response = ec2client.create_route_table(VpcId=vpc_id)
    private_route_table_id = response['RouteTable']['RouteTableId']
    response = ec2client.create_tags(Resources=[private_route_table_id], Tags=[{'Key': 'Name', 'Value': "%s-private-route-table" % (vpc_name)}])
    #
    # Associate public subnets and internet gateway route
    #
    for subnet in private_subnets:
        response = ec2client.associate_route_table(SubnetId=subnet, RouteTableId=private_route_table_id)

    return public_route_table_id, private_route_table_id

#
# Create basic security groups
#
def create_security_groups(vpc_name, vpc_id):
    group_name = "%s-sg" % (vpc_name)
    description = group_name
    response = ec2client.create_security_group(GroupName=group_name, Description=description, VpcId=vpc_id)
    group_id = response['GroupId']
    response = ec2client.create_tags(Resources=[group_id], Tags=[{'Key': 'Name', 'Value': group_name}])

    response = ec2client.authorize_security_group_ingress(GroupId=group_id, IpPermissions=[{ 'IpProtocol': '-1', 'FromPort': -1, 'ToPort': -1, 'UserIdGroupPairs': [{ 'GroupId': group_id }]}])

    return group_id

#
# Create s3 bucket and CloudFront Distribution
#
def create_cloutfront():
    pass

#
# Creat Elastic File System in VPC
#
def create_elastic_filesystem():
    pass

#
# Do VPC creation
#
availability_zone_names = list_availability_zone_names()
vpc_id = create_vpc(cidr_block=cidr_block, vpc_name=vpc_name)
public_subnets, private_subnets = create_subnets(vpc_name=vpc_name, vpc_id=vpc_id, cidr_block=cidr_block, availability_zones=availability_zone_names, subnet_prefix_len=subnet_prefix_len)
igw_id = create_igw(vpc_name=vpc_name, vpc_id=vpc_id)
create_route_tables(vpc_name=vpc_name, vpc_id=vpc_id, igw_id=igw_id, public_subnets=public_subnets, private_subnets=private_subnets)
security_group_id = create_security_groups(vpc_name=vpc_name, vpc_id=vpc_id)

print("\n\nRegion Id: ", region)
print("VPC Id: ", vpc_id)
print("Security Group Id: ", security_group_id)
print("Public subnets: ", public_subnets)
print("Private subnets: ", private_subnets)
print("\n\nRun the following script in the terminal to launch your beanstalk environment: \n\n", "python3 ./create_beanstalk_with_eb_api.py %s %s %s \"%s\"" % (region, vpc_id, security_group_id, public_subnets))
exit(0)