#!/usr/bin/python
#
# update_upstream.py
#
# Attempts to find the private ip associated with an EC2 instance based
# on a tag, and then updates the associated Nginx upstream
# config file
#
# Assumptions:
#   - Script does nothing if it doesn't find any instances with specified tag
#   - Script will just take the first IP if it finds multiple instances
#   - Nginx upstream config directory is hardcoded
#   - Name of the upstream config file is assumed to be {{service}}.conf
#   - Assume instance profile of EC2 instance this runs on has permission
#     to do ec2:Describe*
#   - Requires boto3 (pip install boto3)
#
# Usage examples:
#
# ./update_upstream.py -e dev -s service -k Role -v service -p 433

import argparse
import boto3
import os.path
import re
import requests
import sys

NGINX_UPSTREAM_DIR = '/etc/nginx/conf.d/upstreams/'

def update_upstream_conf(config_file, upstream_host, upstream_port):
    if not os.path.exists(config_file):
        print "Could not find Nginx upstream config file: %s" % config_file
        sys.exit(1)
    data = ''
    with open(config_file, 'r') as f:
        data = f.read()
    print "Updating upstream config %s with host %s and port %s" % (config_file, upstream_host, str(upstream_port))
    new_data = re.sub(r'server\s+[\w\d\.]+:\d+', 'server ' + upstream_host + ':' + str(upstream_port), data, flags=re.IGNORECASE)
    with open(config_file, 'w') as f:
        f.write(new_data)

def list_private_ips_by_tag(tagkey, tagvalue):
    ec2 = boto3.client('ec2', region_name='us-west-2')
    filters = []
    filters.append({'Name': 'tag:'+tagkey, 'Values': [tagvalue]})
    vpc_id = get_vpc_id()
    if vpc_id:
        filters.append({'Name': 'vpc-id', 'Values': [vpc_id]})
    resp = ec2.describe_instances(Filters=filters)
    iplist = []
    for reservation in resp['Reservations']:
        for instance in reservation['Instances']:
            iplist.append(instance['PrivateIpAddress'])
    return iplist

def get_vpc_id():
    interface_req_url = 'http://169.254.169.254/latest/meta-data/network/interfaces/macs/'
    resp = requests.get(interface_req_url)
    vpc_req_url = interface_req_url + resp.text + 'vpc-id'
    resp1 = requests.get(vpc_req_url)
    return resp1.text

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update Nginx upstream configs')
    parser.add_argument('-e', '--env', dest='env', help='Environment')
    parser.add_argument('-s', '--service', dest='service', help='Service name (name of nginx upstream config file')
    parser.add_argument('-p', '--port', dest='port', default=80, help='Service port')
    parser.add_argument('-k', '--tagkey', dest='tagkey', help='EC2 tag key')
    parser.add_argument('-v', '--tagval', dest='tagval', help='EC2 tag value')
    args = parser.parse_args()

    private_ip = list_private_ips_by_tag(args.tagkey, args.tagval)
    if not private_ip:
        print "No instances with tag:key=%s and tag:val=%s found" % (args.tagkey, args.tagval)
        sys.exit(1)

    update_upstream_conf(NGINX_UPSTREAM_DIR + args.service + '.conf', private_ip[0], args.port)
