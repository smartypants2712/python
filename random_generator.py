from __future__ import print_function
import json
import random
import string

def lambda_handler(event, context):
    characters = string.ascii_letters + '!@#$%^&*()[]{}'
    length = event['length']
    return ''.join(random.SystemRandom().choice(characters) for _ in range(length))
