import requests
import json


def web_design_standards_utility(domain):
    payload = {"domain":domain}
    headers = {"Content-Type":"application/json"}
    result = requests.get(
        "https://domain-scan-python-services.app.cloud.gov/services/web-design-standards",
        params=payload,
        headers=headers)
    return json.loads(result.text)
    

def test_web_design_standards_false_false():
    zombocom = "www.zombo.com"
    zombocom_result = web_design_standards_utility(zombocom)
    assert {"uswds":False, "https": False} == zombocom_result


def test_web_design_standards_true_true():
    uswds = "standards.usa.gov"
    uswds_result = web_design_standards_utility(uswds)
    assert {"uswds":True, "https": True} == uswds_result


def test_web_design_standards_false_true():
    treasury = "www.treasury.gov"
    treasury_result = web_design_standards_utility(treasury)
    assert {"uswds":False, "https": True} == treasury_result


# It is hard to find a *.gov that doesn't implement https
# so it's a hard case to test.
