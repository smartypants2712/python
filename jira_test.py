from jira import JIRA
import requests

JIRA_BASE_URL = 'https://simonso.atlassian.net'
JIRA_AUTH = ('admin', '#nG&AMm2IH$M3UO7k!')

def get_project_versions(jira, project):
    versions = jira.project_versions(project)
    return [v.name for v in versions]

def get_issues_with_label(jira, label):
    results = jira.search_issues('labels = ' + label)
    return [i.key for i in results]

# Directly invoking the JIRA API using Requests
# jira-python calls were waaay too slow
def add_fix_version(issue, version):
    print "Adding %s to %s Fix Versions" % (version, issue)
    url = 'https://simonso.atlassian.net/rest/api/2/issue/' + issue
    data = {
        "update": {
            "fixVersions": [
                {
                    "add": { "name": version }
                }
            ]
        }
    }
    r = requests.put(url, auth=JIRA_AUTH, headers={ "Content-Type": "application/json" }, json=data)
    print "HTTP " + str(r.status_code)

j = JIRA(server=JIRA_BASE_URL, basic_auth=JIRA_AUTH)

label = 'fix-gms8.0.0'

issues = get_issues_with_label(j, label)
print "Issues with label " + label + ": " + ', '.join(issues)

for issue in issues:
    project_key = issue.split('-')[0]
    versions = get_project_versions(j, project_key)
    print "Project versions: " + ', '.join(versions)
    version = label.split('-')[1]
    if version not in versions:
        print "%s is not in list of versions" % version
        response = j.create_version(version, project_key)
        print response
    add_fix_version(issue, version)

