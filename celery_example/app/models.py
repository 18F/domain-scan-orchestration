from app import db
    

class Domains(db.Model):
    """
    This is where the list of current domains to scan is stored.
    We can see when this domain was added to the list
    
    Parameters:
    @domain - a domain to scan
    
    @timestamp - when the domain was added to the database
    """
    __tablename__ = "domains"
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String)
    timestamp = db.Column(db.DateTime)
    
    def __init__(self, domain, timestamp):
        self.domain = domain
        self.timestamp = timestamp
        
    def __str__(self):
        return "< domain: {}>".format(repr(self.domain))

class USWDS(db.Model):
    """
    Information relating to scans for the us web design standards.
    There will be multiple entries for the same domain, the only certain difference
    will be the timestamp, which will be unique to each date a scan occurred.
    ## The following 4 lines are not related to documentation, but are good thoughts
    ## think about where to put this
    I think it will be interesting to see the results of scans over time.
    This way we can have a more informed security posture over time.
    Additionally, this allows us to monitor whether things are
    improving or getting worse.

    Parameters:
    @domain - the domain that was scanned
    
    @uswds - a boolean - 
    The result of a scan. 
    If True the web design standards are present on the homepage
    
    @https - a boolean - 
    The result of a scan. 
    If True the website's homepage responds to https requests
    
    @timestamp - a datetime object -
    When the scan took place
    """
    __tablename__ = 'uswds'
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String)
    uswds = db.Column(db.Boolean)
    https = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)

    def __init__(self, domain, uswds, https, timestamp):
        self.domain = domain
        self.uswds = uswds
        self.https = https
        self.timestamp = timestamp

    def __str__(self):
        return "< domain: {}".format(repr(self.domain))
