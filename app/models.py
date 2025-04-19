from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    contributions = db.relationship('Contribution', backref='user', lazy=True)
    withdrawals = db.relationship('Withdrawal', backref='user', lazy=True, foreign_keys='Withdrawal.user_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    contribution_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Contribution by {self.user_id} on {self.contribution_date}>'

class Withdrawal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    approval_status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')
    approval_date = db.Column(db.DateTime)
    approved_by_admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    approved_by_admin = db.relationship('User', foreign_keys=[approved_by_admin_id], backref='approved_withdrawals')

    def __repr__(self):
        return f'<Withdrawal by {self.user_id} on {self.request_date}>'