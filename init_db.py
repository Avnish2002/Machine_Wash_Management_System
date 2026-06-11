from app import app
from extensions import db
import models
from models import Offer

with app.app_context():
    db.create_all()
    # Seed some offers if none exist
    if Offer.query.count() == 0:
        db.session.add_all([
            Offer(title="Monsoon Mega Wash", description="20% off on all exterior washes this week!"),
            Offer(title="Premium + Interior Combo", description="Save ₹200 when you book both together."),
            Offer(title="Loyalty Deal", description="Every 5th wash is FREE for registered users.")
        ])
        db.session.commit()
    print("✅ Database initialized and sample offers added.")
