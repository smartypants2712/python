#!/usr/bin/python

import argparse
import base64
import boto3
import hashlib
import hmac
import logging
import sys
from time import strftime

REGION = "us-west-2"
SERVICE = "s3"
EXAMPLE_STRING_TO_SIGN = "AWS4-HMAC-SHA256\n20150830T123600Z\n20150830/us-east-1/iam/aws4_request\nf536975d06c0309214f805bb90ccff089219ecd68b2577efef23edd43b7e1a59"
EXAMPLE_CREQ = "GET\n/\nAction=ListUsers&Version=2010-05-08\ncontent-type:application/x-www-form-urlencoded; charset=utf-8\nhost:iam.amazonaws.com\nx-amz-date:20150830T123600Z\n\ncontent-type;host;x-amz-date\ne3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

session = boto3.Session()
creds = session.get_credentials()
creds = creds.get_frozen_credentials()
date = strftime("%Y%m%dT%H%M%SZ")

def create_auth_header(signature):
    logging.info("Create Authorization header...")
    header = "AWS4-HMAC-SHA256" + " " + \
            "Credential=" + creds.access_key + "/" + strftime("%Y%m%d") + "/" + \
            REGION + "/" + SERVICE + "/" + "aws4_request,SignedHeaders=content-type;host;x-amz-content-sha256;x-amz-date;x-amz-security-token,Signature=" + signature
    logging.debug("Authorization header: %s" % header)
    return header

def create_signing_key(secret_key=creds.secret_key, date=strftime("%Y%m%d")):
    logging.info("Create signing key...")
    logging.debug("Secret Key: %s" % secret_key)
    date_key = hmac_sha256("AWS4" + str(secret_key), date).digest()
    date_region_key = hmac_sha256(date_key, REGION).digest()
    date_region_service_key = hmac_sha256(date_region_key, SERVICE).digest()
    signing_key = hmac_sha256(date_region_service_key, "aws4_request").digest()
    signing_key_hex = hmac_sha256(date_region_service_key, "aws4_request").hexdigest()
    logging.debug("Signing Key (hex): %s" % signing_key_hex)
    return signing_key

def hmac_sha256(key, data):
    return hmac.new(key, msg=data, digestmod=hashlib.sha256)

def create_string_to_sign(canonical_request):
    logging.info("Create string to sign...")
    scope = strftime("%Y%m%d") + "/" + REGION + "/" + SERVICE + "/aws4_request"
    string_to_sign = "AWS4-HMAC-SHA256" + "\n" + date + "\n" + scope + "\n" + \
            hashlib.sha256(canonical_request).hexdigest()
    logging.debug("\n----- BEING STRING TO SIGN -----\n%s\n----- END STRING TO SIGN -----" % string_to_sign)
    return string_to_sign

def create_headers(bucket, content_hash):
    logging.info("Create headers...")
    host = bucket + ".s3.amazonaws.com"
    security_token = creds.token
    headers = "content-type:application/x-www-form-urlencoded; charset=utf-8" + "\n" + \
            "host:" + host + "\n" + \
            "x-amz-content-sha256:" + content_hash + "\n" + \
            "x-amz-date:" + date + "\n" + \
            "x-amz-security-token:" + security_token
    logging.debug("\n----- BEGIN REQUEST HEADERS -----\n%s\n----- END REQUEST HEADERS -----" % headers)
    return headers

def create_canonical_req(bucket, request_payload="", http_request_method="GET", uri="/", query_string=""):
    logging.info("Create canonical request...")
    signed_headers = "content-type;host;x-amz-content-sha256;x-amz-date;x-amz-security-token"
    h = hashlib.sha256(request_payload).hexdigest()
    headers = create_headers(bucket, h)
    canonical_req = http_request_method + "\n" + \
                    uri + "\n" + \
                    query_string + "\n" + \
                    headers + "\n\n" + \
                    signed_headers + "\n" + h
    logging.debug("\n----- BEGIN CANONICAL REQUEST -----\n%s\n----- END CANONICAL REQEUST -----" % canonical_req)
    return canonical_req

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate signature (authorization header) for AWS REST calls')
    parser.add_argument('-b', '--bucket', dest='bucket', default='default', help='AWS S3 bucket name')
    parser.add_argument('-p', '--path', dest='path', default='/', help='Path to S3 object')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode')
    args = parser.parse_args()

    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    logging.basicConfig(stream=sys.stderr, level=log_level)

    creq = create_canonical_req(args.bucket, uri=args.path)
    string = create_string_to_sign(creq)
    key = create_signing_key()
    signature = hmac_sha256(key, string).hexdigest()
    logging.debug("Signature: %s" % signature)
    create_auth_header(signature)