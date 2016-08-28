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
# Files created/overwritten by script
#
bucket_policy="bucket-policy.json"
distribution_config="cloud-front-distribution.json"

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
  "DefaultRootObject": "index.html",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-${bucket_name}",
        "DomainName": "${distribution_domain}",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "${bucket_name}",
    "ForwardedValues": {
      "QueryString": true,
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


# aws s3 sync ${local_distribution_content} "s3://${bucket_name}/${distribution_name}/" --delete