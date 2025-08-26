from .db_instance import db


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), unique=True, nullable=True, index=True)
    telegram_tag = db.Column(db.String(60), unique=True, nullable=True, index=True)
    flight_preferences = db.relationship("FlightPreference", back_populates="user", cascade="all, delete-orphan")
    notification_preferences = db.relationship("NotificationPreference", back_populates="user", cascade="all, delete-orphan")

class FlightPreference(db.Model):
    __tablename__ = 'flight_preferences'
    preference_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    target_departure = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    departure_airport = db.Column(db.String(4), nullable=False)
    arrival_airport = db.Column(db.String(4), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    seat_class = db.Column(db.String(20), nullable=False)
    max_price = db.Column(db.Float, nullable=True)
    preferred_airline = db.Column(db.String(100), nullable=True)
    user = db.relationship("User", back_populates="flight_preferences")

class NotificationPreference(db.Model):
    __tablename__ = 'notification_preferences'
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    method = db.Column(db.String(50), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    user = db.relationship("User", back_populates="notification_preferences")