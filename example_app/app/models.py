from app import db

class Gathered(db.Model):

    __tablename__ = 'filenames'
    id = db.Column(db.Integer, primary_key=True)
    placeholder = db.Column(db.String)
    
    def __init__(self, placeholder):
        self.placeholder = placeholder
        
