#!/usr/bin/python
import requests
import json
import argparse
import urllib3

urllib3.disable_warnings()


### Ready arguments from command line ###
## TO DO ##
# To manager nsxmgr name, user id , password ..may be Tier0 url?

#ap = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
#                                epilog="Welcome to sddc_import_export!\n"
#                                "python export_import.py -u username -p password -m nsxmgr\n\n")
#ap.add_argument("-u", "--user", required=False, help="NSX Manager user ")
#ap.add_argument("-p", "--password", required=False, help="NSX Manager password ")
#ap.add_argument("-m","--nsx-mgr", required=False,help="NSX Manager name ")
#
#args = ap.parse_args(args)

srevproxyurl='https://nsxmgr-01a.corp.local'
curCursor = ''
pageSize = 1000
### Source SDDC URL's ###
smgwgroupsurl = '%s/policy/api/v1/infra/domains/default/groups?page_size=%s&cursor=%s' %(srevproxyurl,pageSize,curCursor)
smgwurl = '%s/policy/api/v1/infra/domains/default/gateway-policies/FTP_POLICY/rules' %(srevproxyurl)
smgwpolicyurl = '%s/policy/api/v1/infra/domains/default/gateway-policies' %(srevproxyurl)
sservicesurl = '%s/policy/api/v1/infra/services?page_size=%s&cursor=%s' %(srevproxyurl,pageSize,curCursor)

sfwDump = open("sourceRules.json", "a+")
### Get Source MGW Groups ###
print("MGW Groups")
mgroupsresp = requests.get(smgwgroupsurl,auth=('admin','VMware1!VMware1!'),verify=False)
mg = json.loads(mgroupsresp.text)
mgroups = mg["results"]
if mg["result_count"] > pageSize:
    curCursor = mg["cursor"]
    smgwgroupsurl = '%s/policy/api/v1/infra/domains/default/groups?page_size=%s&cursor=%s' %(srevproxyurl,pageSize,curCursor)
    while "cursor" in mg:
        mgroupsresp = requests.get(smgwgroupsurl,auth=('admin','VMware1!VMware1!'),verify=False)
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
servicesresp = requests.get(sservicesurl,auth=('admin','VMware1!VMware1!'),verify=False)
srv = json.loads(servicesresp.text)
services = srv["results"]

### Filter out system Services ###
print("Services")
if srv["result_count"] > pageSize:
    curCursor = srv["cursor"]
    sservicesurl = '%s/policy/api/v1/infra/services?page_size=%s&cursor=%s' %(srevproxyurl,pageSize,curCursor)
    while "cursor" in srv:
        servicesresp = requests.get(sservicesurl,auth=('admin','VMware1!VMware1!'),verify=False)
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
mgwresponse = requests.get(smgwurl,auth=('admin','VMware1!VMware1!'),verify=False)
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
mgwpolicyresponse = requests.get(smgwpolicyurl,auth=('admin','VMware1!VMware1!'),verify=False)
n = json.loads(mgwpolicyresponse.text)
mgwpolicies = n["results"]
print(json.dumps(mgwpolicies,indent=4))

for pid in mgwpolicies:
    policyid = pid['id']
    print (" === Rules for  Policy ID:  ===" + policyid)
    scgwurl = '%s/policy/api/v1/infra/domains/default/gateway-policies/%s/rules' %(srevproxyurl,policyid)
    cgwresponse = requests.get(scgwurl,auth=('admin','VMware1!VMware1!'),verify=False)
    c = json.loads(cgwresponse.text)
    cgwrules = c["results"]
    print(json.dumps(cgwrules,indent=4))
    sfwDump.write(cgwresponse.text)
    for rule in cgwrules:
        if rule["id"]== "FTP_RULE":
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
            payload["scope"] = ["/infra/tier-0s/Tier-0-Ansible"]
            payload["action"] = rule["action"]
            payload["services"] = rule["services"]
            payload["destination_groups"] = rule["destination_groups"]
            json_data = json.dumps(payload)
            print("===========================")
            print(json.dumps(payload,indent=4))
            print("===========================")
            headers={'content-type': 'application/json'}
            createfwruleresp = requests.patch(updatedscgwurl,auth=('admin','VMware1!VMware1!'),verify=False,data=json_data,headers=headers)
            print(createfwruleresp.text)
            payload = {}

