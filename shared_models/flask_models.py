from sqlalchemy import Text, Column, String
from shared_models import db
class Pdflist(db.Model):
    __tablename__ = 'pdflist'
    id = db.Column(db.Integer, primary_key=True)
    pdf_name = Column(String(300))
    pdf_content = Column(Text)



    def __repr__(self):
        return f'<User {self.username}>'