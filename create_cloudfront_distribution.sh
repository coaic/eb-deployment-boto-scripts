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
    "DistributionConfig": {
        "CallerReference": "",
        "Aliases": {
            "Quantity": 0,
            "Items": [
                ""
            ]
        },
        "DefaultRootObject": "",
        "Origins": {
            "Quantity": 0,
            "Items": [
                {
                    "Id": "S3-${distribution_domain}",
                    "DomainName": "${distribution_domain}",
                    "OriginPath": "${distribution_prefix}",
                    "CustomHeaders": {
                        "Quantity": 0,
                        "Items": [
                            {
                                "HeaderName": "",
                                "HeaderValue": ""
                            }
                        ]
                    },
                    "S3OriginConfig": {
                        "OriginAccessIdentity": ""
                    },
                    "CustomOriginConfig": {
                        "HTTPPort": 80,
                        "HTTPSPort": 443,
                        "OriginProtocolPolicy": "http-only",
                        "OriginSslProtocols": {
                            "Quantity": 0,
                            "Items": [
                                ""
                            ]
                        }
                    }
                }
            ]
        },
        "DefaultCacheBehavior": {
            "TargetOriginId": "S3-${distribution_domain}",
            "ForwardedValues": {
                "QueryString": false,
                "Cookies": {
                    "Forward": "none",
                    "WhitelistedNames": {
                        "Quantity": 0,
                        "Items": [
                            ""
                        ]
                    }
                },
                "Headers": {
                    "Quantity": 0,
                    "Items": [
                        ""
                    ]
                }
            },
            "TrustedSigners": {
                "Enabled": false,
                "Quantity": 0,
                "Items": [
                    ""
                ]
            },
            "ViewerProtocolPolicy": "allow-all",
            "MinTTL": 0,
            "AllowedMethods": {
                "Quantity": 2,
                "Items": [
                    "GET",
                    "HEAD"
                ],
                "CachedMethods": {
                    "Quantity": 2,
                    "Items": [
                        "GET",
                        "HEAD"
                    ]
                }
            },
            "SmoothStreaming": false,
            "DefaultTTL": 0,
            "MaxTTL": 0,
            "Compress": true
        },
        "CacheBehaviors": {
            "Quantity": 0,
            "Items": [
                {
                    "PathPattern": "",
                    "TargetOriginId": "",
                    "ForwardedValues": {
                        "QueryString": true,
                        "Cookies": {
                            "Forward": "",
                            "WhitelistedNames": {
                                "Quantity": 0,
                                "Items": [
                                    ""
                                ]
                            }
                        },
                        "Headers": {
                            "Quantity": 0,
                            "Items": [
                                ""
                            ]
                        }
                    },
                    "TrustedSigners": {
                        "Enabled": true,
                        "Quantity": 0,
                        "Items": [
                            ""
                        ]
                    },
                    "ViewerProtocolPolicy": "",
                    "MinTTL": 0,
                    "AllowedMethods": {
                        "Quantity": 0,
                        "Items": [
                            ""
                        ],
                        "CachedMethods": {
                            "Quantity": 0,
                            "Items": [
                                ""
                            ]
                        }
                    },
                    "SmoothStreaming": true,
                    "DefaultTTL": 0,
                    "MaxTTL": 0,
                    "Compress": true
                }
            ]
        },
        "CustomErrorResponses": {
            "Quantity": 0,
            "Items": [
                {
                    "ErrorCode": 0,
                    "ResponsePagePath": "",
                    "ResponseCode": "",
                    "ErrorCachingMinTTL": 0
                }
            ]
        },
        "Comment": "",
        "Logging": {
            "Enabled": true,
            "IncludeCookies": true,
            "Bucket": "",
            "Prefix": ""
        },
        "PriceClass": "",
        "Enabled": true,
        "ViewerCertificate": {
            "CloudFrontDefaultCertificate": true,
            "IAMCertificateId": "",
            "ACMCertificateArn": "",
            "SSLSupportMethod": "",
            "MinimumProtocolVersion": "",
            "Certificate": "",
            "CertificateSource": ""
        },
        "Restrictions": {
            "GeoRestriction": {
                "RestrictionType": "none",
                "Quantity": 0,
                "Items": [
                    ""
                ]
            }
        },
        "WebACLId": ""
    }
}
EOF
    set -x
    aws cloudfront create-distribution --distribution-config file://$(pwd)/${distribution_config}
    #echo $(cat ${distribution_config})


# aws s3 sync ${local_distribution_content} "s3://${bucket_name}/${distribution_name}/" --delete