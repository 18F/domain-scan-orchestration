from app import celery_obj
from app.models import Domains, USWDS
from app import db
import datetime as dt

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

