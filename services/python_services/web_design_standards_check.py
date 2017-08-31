import lxml.html
import requests

# This checks static sites only for now
# we'll need to use selenium for react sites
# or javascript
def uswds_checker(domain):
    https = True
    url = "https://"+domain
    try:
        response = requests.get(url).text
    except requests.exceptions.SSLError:
        https = False
        url = "http://"+domain
        response = requests.get(url).text
    html = lxml.html.fromstring(response)
    if len(html.xpath("//*[contains(@class, 'usa-')]")) > 0:
        return {"uswds":True, "https":https}
    else:
        return {"uswds":False, "https":https}


