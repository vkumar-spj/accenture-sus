#!/usr/bin/python
import requests
import json
import argparse
import urllib3
import sys
#from ConfigParser import ConfigParser

urllib3.disable_warnings()


### Ready arguments from command line ###
my_parser = argparse.ArgumentParser(fromfile_prefix_chars='@',description='NSX Tier1 to Tier0 FW rule migration, Provide NSX Manager crednet
ails,upon successful rules are logging into a json file in same directory',
                                    epilog='Happy migration ! :)')
my_parser.add_argument('--nsxmgr',
                       help='NSX Manager Name,preferaly FQDN',required=True)

my_parser.add_argument('--user',
                       help='NSX Manager UserID',default='admin',required=True)

my_parser.add_argument('--password',
                       help='NSX Manager password',default='VMware1!VMware1!',required=True)

my_parser.add_argument('--tier0path',
        help='Tier0 Path from NSX Manager Ex:/infra/tier-0s/Tier-0',default='/infra/tier-0s/Tier-0-Ansible',required=False)

my_parser.add_argument('--tier1path',
        help='Tier1 Path from NSX Manager Ex:/infra/tier-1s/Tier-1',default='tier1',required=False)
args = my_parser.parse_args()
# Priting arguments
print(args)


srevproxyurl='https://%s' %(args.nsxmgr)
print("URL is " + srevproxyurl)
curCursor = ''
pageSize = 1000
### Source SDDC URL's ###
smgwgroupsurl = '%s/policy/api/v1/infra/domains/default/groups?page_size=%s&cursor=%s' %(srevproxyurl,pageSize,curCursor)
smgwpolicyurl = '%s/policy/api/v1/infra/domains/default/gateway-policies' %(srevproxyurl)
sservicesurl = '%s/policy/api/v1/infra/services?page_size=%s&cursor=%s' %(srevproxyurl,pageSize,curCursor)

sfwDump = open("sourceRules.json", "a+")
### Get Source MGW Groups ###
print("MGW Groups")
try:
    mgroupsresp = requests.get(smgwgroupsurl,auth=(args.user,args.password),verify=False)
except requests.ConnectionError as exception:
    print("Unable to reach  URL ,verify  nsx manager name is valid and reachable from browser")
    print("\nReceived following error making API call:" )
    raise SystemExit(exception)

mg = json.loads(mgroupsresp.text)
mgroups = mg["results"]
if mg["result_count"] > pageSize:
    curCursor = mg["cursor"]
    smgwgroupsurl = '%s/policy/api/v1/infra/domains/default/groups?page_size=%s&cursor=%s' %(srevproxyurl,pageSize,curCursor)
    while "cursor" in mg:
        try:
            mgroupsresp = requests.get(smgwgroupsurl,auth=('admin','VMware1!VMware1!'),verify=False)
            mgroupsresp = requests.get(smgwgroupsurl,auth=(args.user,args.password),verify=False)
            print("Entered here")
        except requests.ConnectionError as exception:
            print("Verify URL and nsx manager name is valid")
            raise SystemExit(exception)

        mg = json.loads(mgroupsresp.text)
        mgroups = mg["results"]
        if "cursor" in mg:
            curCursor = mg["cursor"]
        smgwgroupsurl = '%s/policy/api/v1/infra/domains/default/groups?page_size=%s&cursor=%s' %(srevproxyurl,pageSize,curCursor)
        ### Filter out system groups ###
        for group in mgroups:
            if group["_create_user"]!= "admin" and group["_create_user"]!="admin;admin":
                print(json.dumps(group,indent=4))
for group in mgroups:
            if group["_create_user"]!= "admin" and group["_create_user"]!="admin;admin":
                print(json.dumps(group,indent=4))

### Get Source SDDC Firewall Services ###
servicesresp = requests.get(sservicesurl,auth=(args.user,args.password),verify=False)
srv = json.loads(servicesresp.text)
services = srv["results"]

### Filter out system Services ###
print("Services")
if srv["result_count"] > pageSize:
    curCursor = srv["cursor"]
    sservicesurl = '%s/policy/api/v1/infra/services?page_size=%s&cursor=%s' %(srevproxyurl,pageSize,curCursor)
    while "cursor" in srv:
        servicesresp = requests.get(sservicesurl,auth=(args.user,args.password),verify=False)
        srv = json.loads(servicesresp.text)
        services = srv["results"]
        if "cursor" in srv:
            curCursor = srv["cursor"]
        sservicesurl = '%s/policy/api/v1/infra/services?page_size=%s&cursor=%s' %(srevproxyurl,pageSize,curCursor)
        ### Filter out system services ###
        for service in services:
            if service["_create_user"]!= "admin" and service["_create_user"]!="admin;admin" and service["_create_user"]!="system":
                print(json.dumps(service,indent=4))
for service in services:
    if service["_create_user"]!= "admin" and service["_create_user"]!="admin;admin" and service["_create_user"]!="system":
        print(json.dumps(service,indent=4))

### Get Management Gateway Firewall Rules ###
mgwresponse = requests.get(smgwpolicyurl,auth=(args.user,args.password),verify=False)
m = json.loads(mgwresponse.text)
mgwrules = m["results"]

### Filter out system Rules ###
curCursor = ''
print("MGW Rules")
for rule in mgwrules:
#    if rule["_create_user"]!= "admin" and rule["_create_user"]!="system":
#        print(json.dumps(rule,indent=4))
    print(json.dumps(rule,indent=4))



## All rules iterating over the policies
mgwpolicyresponse = requests.get(smgwpolicyurl,auth=(args.user,args.password),verify=False)
n = json.loads(mgwpolicyresponse.text)
mgwpolicies = n["results"]
print(json.dumps(mgwpolicies,indent=4))

for pid in mgwpolicies:
    policyid = pid['id']
    print (" === Rules for  Policy ID  === :" + policyid)
    scgwurl = '%s/policy/api/v1/infra/domains/default/gateway-policies/%s/rules' %(srevproxyurl,policyid)
    cgwresponse = requests.get(scgwurl,auth=(args.user,args.password),verify=False)
    c = json.loads(cgwresponse.text)
    cgwrules = c["results"]
    print(json.dumps(cgwrules,indent=4))
    sfwDump.write(cgwresponse.text)
    for rule in cgwrules:
#        if not rule["id"].startswith('default') or rule['policyid'].find("Policy_Default"):
        if not rule["id"].startswith('default'):
            ruleid=rule["id"]
            updatedscgwurl = '%s/policy/api/v1/infra/domains/default/gateway-policies/%s/rules/%s' %(srevproxyurl,policyid,ruleid)
            print("Printng FTP_RULE details")
            print(json.dumps(rule,indent=4))
            print("nameof the rule"+rule["display_name"])
            print(rule["source_groups"])
            print(rule["destination_groups"])
            print(rule["services"])
            print(rule["action"])
            payload = {}
            if rule.get("tags"):
                payload["tags"] = rule["tags"]
            if rule.get("description"):
                payload["description"] = rule["description"]
            payload["id"] = rule["id"]
            payload["path"] = rule["path"]
            payload["source_groups"] = rule["source_groups"]
            payload["resource_type"] = rule["resource_type"]
            payload["display_name"] = rule["display_name"]
            payload["scope"] = [args.tier0path]
            payload["action"] = rule["action"]
            payload["services"] = rule["services"]
            payload["destination_groups"] = rule["destination_groups"]
            json_data = json.dumps(payload)
            print("===========================")
            print(json.dumps(payload,indent=4))
            print("===========================")
            headers={'content-type': 'application/json'}
            createfwruleresp = requests.patch(updatedscgwurl,auth=(args.user,args.password),verify=False,data=json_data,headers=headers)
            print(createfwruleresp.text)
            payload = {}


                                                                              

