from app import celery_obj
from app.models import Domains, USWDS
from app import db
import datetime as dt
import pandas as pd
from io import StringIO
from app import censys_api
import requests
import json
import os
import boto
from boto.s3.key import Key

@celery_obj.task
def uswds():
    """
    Runs the us web design standards checker against the uploaded list of domains.
    """
    results = {}
    for domain in Domains.query.all():
        payload = {"domain":domain.domain}
        headers = {"Content-Type":"application/json"}
        result = requests.get(
            "https://domain-scan-python-services.app.cloud.gov/services/web-design-standards",
            params=payload,
        headers=headers)
        result = json.loads(result.text)
        uswds = USWDS(domain.domain, result["uswds"], result["https"], dt.datetime.now())
        db.session.add(uswds)
        db.session.commit()
        results[domain.domain] = result
    return results #maybe?


def string_to_list(string):
    return string.split("\n")

def string_to_df_to_list(string):
    data = StringIO(string)
    df = pd.read_csv(data, sep=",")
    return list(df["Domain Name"])

def upload_to_s3(csv_file_contents, bucket_name):
    vcap_services = os.getenv("VCAP_SERVICES")
    vcap_services = json.loads(vcap_services)
    bucket = vcap["s3"][0]["credentials"]["bucket"]
    access_key_id = vcap["s3"][0]["credentials"]["access_key_id"]
    region = vcap["s3"][0]["credentials"]["region"]
    secret_access_key = vcap["s3"][0]["credentials"]["secret_access_key"]
    connection = boto.s3.connect_to_region(
        region,
        access_key_id,
        secret_access_key
    )
    bucket = connection.get_bucket(bucket)
    key = Key(bucket=bucket, name=bucket_name)
    f = StringIO(csv_file_contents)
    try:
        key.send_file(f)
        return "success"
    except:
        return "failed"
    
@celery_obj.task
def gatherer():
    """
    Grabs from dap, censys, eot2016, and parent domains of .gov
    """
    data = {}
    options = json.load(open("options.creds","r"))
    censys_list = censys_api.gather(".gov", options)
    censys_list = list(set(censys_list))
    censys_list = [elem for elem in censys_list if ".gov" in elem]
    eot2016 = requests.get("https://github.com/GSA/data/raw/gh-pages/end-of-term-archive-csv/eot-2016-seeds.csv")
    eot2016_string = eot2016.text
    eot2016_list = string_to_list(eot2016_string)

    dap = requests.get("https://analytics.usa.gov/data/live/sites-extended.csv")
    dap_string = dap.text
    dap_list = string_to_list(dap_string)
    dap_list = dap_list[1:]
    dap_list = string_to_list(dap_string)

    parents = requests.get("https://raw.githubusercontent.com/GSA/data/gh-pages/dotgov-domains/current-federal.csv")
    parents_string = parents.text
    parents_list = string_to_df_to_list(parents_string)

    data["eot2016"] = eot2016_list
    data["dap"] = dap_list
    data["parents"] = parents_list

    master_list = parents_list + dap_list + eot2016_list + censys_list
    master_list = list(set(master_list))

    master_data = {
        "eot":[],
        "dap":[],
        "parents":[],
        "domains":[],
        "censys": []
    }
    for domain in master_list:
        master_data["domains"].append(domain)
        master_data["eot"].append(domain in eot2016_list)
        master_data["dap"].append(domain in dap_list)
        master_data["parents"].append(domain in parents_list)
        master_data["censys"].append(domain in censys_list)
    df = pd.DataFrame(master_data)
    s = StringIO()
    df.to_csv(s)
    csv_file_contents = s.getvalue()
    bucket_name = "dotgov_subdomains"
    upload_to_s3(csv_file_contents, bucket_name)
    return s.getvalue()

    

