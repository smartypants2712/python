#!/usr/bin/python

# Helper to export or unset AWS credentials from ~/.aws/credentials
# into environment variables
# 
# Usage:
#   - Set "myprofile" AWS credentials
#       eval $(~/aws_creds.py -p myprofile)
#   - Unset AWS credentials
#       eval $(~/aws_creds.py -u)
#

import argparse
import sys
import ConfigParser

CREDENTIALS_FILE='/Users/simon.so/.aws/credentials'

parser = argparse.ArgumentParser(description='Export or unset AWS credentials')
parser.add_argument('-p', '--profile', dest='profile', default='default', help='AWS credential profile')
parser.add_argument('-u', '--unset', action='store_true', help='Unset environment varibales')
args = parser.parse_args()

if args.unset:
    print 'unset AWS_ACCESS_KEY_ID; unset AWS_SECRET_ACCESS_KEY; unset REGION'
    sys.exit(0)

c = ConfigParser.RawConfigParser()
c.read(CREDENTIALS_FILE)

aws_access_key_id = c.get(args.profile, 'aws_access_key_id')
aws_secret_access_key = c.get(args.profile, 'aws_secret_access_key')
region = c.get(args.profile, 'region')

print 'export AWS_ACCESS_KEY_ID=%s; export AWS_SECRET_ACCESS_KEY=%s; export REGION=%s' % ( aws_access_key_id, aws_secret_access_key, region )
