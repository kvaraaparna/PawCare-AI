from database import db


class SkinDisease(db.Model):
    __tablename__ = "skin_disease"

    disease_name = db.Column(
        db.String(150),
        primary_key=True
    )

    symptoms = db.Column(db.Text)
    causes = db.Column(db.Text)
    suggestions = db.Column(db.Text)
    prevention = db.Column(db.Text)