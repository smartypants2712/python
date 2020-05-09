#!/usr/bin/env python3

import sys
import gimme_aws_creds.main
import gimme_aws_creds.ui

account_alias_id_map = {
    "master": "123456789012",
    "shared-services": "123456789012",
    "network": "123456789012",
    "security": "123456789012",
    "logging": "123456789012",
    "dev": "123456789012",
    "test": "123456789012",
    "stage": "123456789012",
    "prod": "123456789012"
}

account_alias = sys.argv[1]
role_name = sys.argv[2]

if account_alias:
    account_ids = [account_alias_id_map[k]
                   for k in account_alias_id_map if k == account_alias]
else:
    account_ids = [account_alias_id_map[k]
                   for k in account_alias_id_map]

account_id_pattern = "|".join(sorted(set(account_ids)))
role_name_pattern = r"role\/{}".format(role_name) if role_name else ''
pattern = '/:({}):{}/'.format(account_id_pattern, role_name_pattern)
ui = gimme_aws_creds.ui.CLIUserInterface(
    argv=[sys.argv[0], '--profile', 'acme', '--roles', pattern])
creds = gimme_aws_creds.main.GimmeAWSCreds(ui=ui)

for data in creds.iter_selected_aws_credentials():
    creds.write_aws_creds_from_data(data)
