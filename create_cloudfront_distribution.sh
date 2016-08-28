#!/usr/bin/env bash
#
# Create CloudFront distribution using an S3 bucket as an orgin
#
region="us-west-2"
account_id=$(aws ec2 describe-security-groups --group-names 'Default' --query 'SecurityGroups[0].OwnerId' --output text --region ${region})
bucket_name_prefix="shelde-test-distribution"
distribution_domain="${bucket_name_prefix}-${region}-${account_id}.s3.amazonaws.com"
distribution_prefix="/blue"
#
# Access to AWS Console
#
cloudfront_console_uri="https://console.aws.amazon.com/cloudfront/home?region=${region}#distributions:"
#
# Files created/overwritten by script
#
bucket_policy="bucket-policy.json"
distribution_config="cloudfront-distribution.json"

local_distribution_content="cloudfront"

echo "Account Id: ${account_id}"

bucket_name=${bucket_name_prefix}-${region}-${account_id}

if aws s3api head-bucket --bucket "${bucket_name}" 2>/dev/null
then
    echo "Using bucket: s3://${bucket_name}"
else
    echo "Creating bucket: s3://${bucket_name}"
    aws s3 mb "s3://${bucket_name}" --region ${region}
    #
    # Set bucket policy for CloudFront distribution
    #
    cat <<EOF >${bucket_policy}
{
    "Version": "2012-10-17",
    "Id": "Policy1431883602565",
    "Statement": [
        {
            "Sid": "Stmt1431883600330",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${bucket_name}/*"
        }
    ]
}
EOF
    #
    # Wait for bucket creation eventual consistency before making API call on bucket
    #
    echo "Waiting for bucket eventual consistency..."
    sleep 60
    aws s3api put-bucket-policy --bucket ${bucket_name} --policy file://$(pwd)/${bucket_policy}
    #
    # Configure the CloudFront distribution
    #

fi

    cat <<EOF >${distribution_config}
{
  "CallerReference": "${bucket_name}-2016-08-28",
  "Aliases": {
    "Quantity": 0
  },
  "DefaultRootObject": "",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-${bucket_name}",
        "DomainName": "${distribution_domain}",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        },
        "OriginPath": "${distribution_prefix}",
      }
    ]
  },
  "DefaultRootObject": "index.html",
  "PriceClass": "PriceClass_All",
  "Enabled": true,
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-${bucket_name}",
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    },
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    },
    "ViewerProtocolPolicy": "allow-all",
    "MinTTL": 3600
  },
  "CacheBehaviors": {
    "Quantity": 0
  },
  "Comment": "",
  "Logging": {
    "Enabled": false,
    "IncludeCookies": true,
    "Bucket": "",
    "Prefix": ""
  },
  "PriceClass": "PriceClass_All",
  "Enabled": true
}
EOF
    set -x
    aws cloudfront create-distribution --distribution-config file://$(pwd)/${distribution_config}
    #echo $(cat ${distribution_config})
    python3 -c "import webbrowser; webbrowser.open(${cloudfront_console_uri})"

#
# Set default index.html for distribution
#
cat <<EOF >${local_distribution_content}/index.html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8"/>
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />

    <link href="css/bootstrap.css" rel="stylesheet" />
    <link href="css/snakes.css" rel="stylesheet" />

    <title>Default Page for Static Assets in CloudFront</title>
  </head>
  <body>
    <h1>Default Page for Static Assets in CloudFront</h1>
  </body>
</html>
EOF

set -x
aws s3 sync ${local_distribution_content} "s3://${bucket_name}${distribution_prefix}/" --delete