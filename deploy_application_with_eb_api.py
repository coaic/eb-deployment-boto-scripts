#!/usr/local/bin/python3
#
# Create application and launch environment with dummy application running
#
import sys
import boto3
import threading
import datetime
import time
import webbrowser

region = 'us-west-2'
application_war = 'ROOT.war'
account_id = boto3.resource('iam').CurrentUser().arn.split(':')[4]

eb_region_s3_bucket = "elasticbeanstalk-%s-%s" % (region, account_id)

wait_for_green = 5

application_name = 'shelde01'
environment_name = "%s-blue" % (application_name)
application_version = "version_%s" % (str(datetime.datetime.now()).replace(' ','_'))
application_description = 'Intitial version'
war_version = "%s-%s" % (application_version, application_war)

class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._seen_so_far = 0
        self._lock = threading.Lock()
    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            sys.stdout.write(
                "\r%s --> %s bytes transferred" % (
                    self._filename, self._seen_so_far))
            sys.stdout.flush()



ebclient = boto3.client('elasticbeanstalk', region)
s3client = boto3.client('s3', region)

try:
    response = s3client.head_bucket(Bucket=eb_region_s3_bucket)
except Exception as inst:
    print("ERROR: S3 bucket %s does not exist in region %s" % (eb_region_s3_bucket, region))
    exit(1)

#
# Upload .war file to Elastic Beanstalk
#
s3client.upload_file(application_war, eb_region_s3_bucket, war_version, Callback=ProgressPercentage(war_version))
print("\nUpload complete.")


response = ebclient.create_application_version(
    ApplicationName=application_name,
    VersionLabel=application_version,
    Description=application_version,
    SourceBundle={
        'S3Bucket': eb_region_s3_bucket,
        'S3Key': war_version
    },
    AutoCreateApplication=False,
    Process=False
)

response = ebclient.update_environment(EnvironmentName=environment_name, ApplicationName=application_name, VersionLabel=application_version)

url = response['CNAME']
environment_id = response['EnvironmentId']

#
# Open AWS Console to observe Environment progress
#
webbrowser.open_new("https://us-west-2.console.aws.amazon.com/elasticbeanstalk/home?region=us-west-2#/environment/dashboard?applicationName=%s&environmentId=%s" % (application_name, environment_id))

time.sleep(60)
webbrowser.open_new("http://%s" % (url))
exit(0)

