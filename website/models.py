from . import db 
from flask_login import UserMixin

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itemName = db.Column(db.String(100))
    itemDesc = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    transaction = db.relationship('Transaction')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    isAccepted = db.Column(db.Boolean, default=False)
    isCompleted = db.Column(db.Boolean, default=False)
    

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    givingPoints = db.Column(db.Integer)
    contactNum = db.Column(db.String(15))
    item = db.relationship('Item')
    transaction = db.relationship('Transaction')
