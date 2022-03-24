#!/bin/sh

keyfile="<path/to/your/ssh_key_file.pem>"
user="<official IAM username of your instance's distribution>" #check here: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/managing-users.html

if [ $# -ne 1 ]; then
    echo $0: invalid arguments
    exit 1
fi

tag=$1
host=$(aws ec2 describe-instances --filters "Name=tag:$tag,Values=" --query 'Reservations[*].Instances[*].[PublicIpAddress]' --output text)

if [ "$host" ]; then
    exec ssh -i $keyfile $user@$host
else
    echo "Host not found"
fi