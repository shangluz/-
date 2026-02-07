from datetime import datetime
from decimal import Decimal
from flask_login import UserMixin
from sqlalchemy import Numeric
from extensions import db

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50))
    role = db.Column(db.String(20))

    def __repr__(self):
        return f"<User {self.username}>"

class Vehicle(db.Model):
    __tablename__ = "vehicles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, server_default="空闲")

    def __repr__(self):
        return f"<Vehicle {self.plate_number}>"

class Driver(db.Model):
    __tablename__ = "drivers"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))

    def __repr__(self):
        return f"<Driver {self.name}>"

class TransportTask(db.Model):
    __tablename__ = "transport_tasks"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_name = db.Column(db.String(100))
    need_vehicle_type = db.Column(db.String(50))
    need_count = db.Column(db.Integer)
    plan_mileage = db.Column(Numeric(10, 2))
    plan_start_time = db.Column(db.DateTime)
    plan_end_time = db.Column(db.DateTime)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"), nullable=True)
    real_start_time = db.Column(db.DateTime)
    real_end_time = db.Column(db.DateTime)
    real_mileage = db.Column(Numeric(10, 2))
    fuel_used = db.Column(Numeric(10, 2))
    status = db.Column(db.String(20), nullable=False, server_default="待安排")

    vehicle = db.relationship("Vehicle", backref="tasks")
    driver = db.relationship("Driver", backref="tasks")

    def __repr__(self):
        return f"<TransportTask {self.id} {self.client_name}>"

class Accident(db.Model):
    __tablename__ = "accidents"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"), nullable=False)
    accident_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.Text)
    reason = db.Column(db.Text)
    handle_method = db.Column(db.Text)
    cost = db.Column(Numeric(12, 2))
    other_plate = db.Column(db.String(50))

    vehicle = db.relationship("Vehicle", backref="accidents")
    driver = db.relationship("Driver", backref="accidents")

    def __repr__(self):
        return f"<Accident {self.id}>"

def create_tables(app=None):
    if app is None:
        from app import create_app
        app = create_app()
    with app.app_context():
        db.create_all()