#!/usr/local/bin/python3

import argparse
import sys
import configparser
import yaml
import re

CREDENTIALS_FILE = "/Users/simon.so/.aws/credentials"
KUBECONFIG = "/Users/simon.so/.kube/config"

parser = argparse.ArgumentParser(
    description='Write AWS credentials into kubeconfig')
parser.add_argument('-c', '--cluster', dest='cluster',
                    default='shared-services-us-east-1-eks', help='AWS EKS cluster name')
parser.add_argument('-p', '--profile', dest='profile',
                    default='default', help='AWS credential profile')
parser.add_argument('-u', '--unset', action='store_true',
                    help='Unset environment varibales')
args = parser.parse_args()

if args.unset:
    print('unset AWS_ACCESS_KEY_ID; unset AWS_SECRET_ACCESS_KEY; unset AWS_SESSION_TOKEN; unset REGION')
    sys.exit(0)

c = configparser.RawConfigParser()
c.read(CREDENTIALS_FILE)


def find_index(users, cluster_name):
    idx = None
    for i, x in enumerate(users):
        if re.findall(cluster_name, x["name"]):
            print(f"Cluster {cluster_name} found")
            idx = i
            break
    return idx


aws_access_key_id = c.get(args.profile, 'aws_access_key_id')
aws_secret_access_key = c.get(args.profile, 'aws_secret_access_key')
aws_session_token = c.get(args.profile, 'aws_session_token')
region = c.get(args.profile, 'region', fallback='us-east-1')

kubeconfig = {}

print(f"Reading from {KUBECONFIG}")
with open(KUBECONFIG) as f:
    kubeconfig = yaml.load(f, Loader=yaml.FullLoader)

users = kubeconfig["users"]
index = find_index(users, args.cluster)
if index == None:
    print(f"Cluster {args.cluster} not found in {KUBECONFIG}")
    sys.exit(1)

kubeconfig["users"][index]["user"]["exec"]["env"] = [
    {
        "name": "AWS_ACCESS_KEY_ID",
        "value": aws_access_key_id
    },
    {
        "name": "AWS_SECRET_ACCESS_KEY",
        "value": aws_secret_access_key
    },
    {
        "name": "AWS_SESSION_TOKEN",
        "value": aws_session_token
    }
]

print(f"Writing to {KUBECONFIG}")
with open(KUBECONFIG, 'w') as f:
    data = yaml.dump(kubeconfig, f)
print("Done")
