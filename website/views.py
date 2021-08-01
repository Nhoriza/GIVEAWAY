from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for
from .models import Item, Transaction, User
from . import db 
from flask_login import login_required, current_user
from sqlalchemy import and_
import logging
from logging import Formatter, FileHandler

app = Flask(__name__)

file_handler = FileHandler('logging.log')
handler = logging.StreamHandler()
file_handler.setLevel(logging.DEBUG)
handler.setLevel(logging.DEBUG)
file_handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))

handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(handler)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

views = Blueprint('views', __name__)

@views.route('/landing')
@login_required
def landing():
    return render_template('landing.html', user=current_user)

@views.route('/giver', methods=['GET', 'POST'])
@login_required
def giver():
    if request.method == 'POST':
        data = request.form
        itemName = request.form.get('item-name')
        itemDesc = request.form.get('item-desc')

        new_item = Item(itemName=itemName, itemDesc=itemDesc, user_id=current_user.id)
        db.session.add(new_item)
        db.session.commit()

        app.logger.info(current_user.username + ' added items')

    return render_template('giver.html', user=current_user)

@views.route('/transactions', methods=['GET', 'POST'])
def transactions():
    item_transaction = [item_id[0] for item_id in Transaction.query.with_entities(Transaction.item_id).all()]
    items = Item.query.filter(Item.user_id == current_user.id, Item.id.in_(item_transaction))

    transaction_list = []
    transaction_dict = {"transaction_id":"", "receiver_name":"", "receiver_points":"", "receiver_num": "", "item_id":"", "transaction_accepted": "", "transaction_completed": ""}

    if items: 
        for item in items:
            transactions = Transaction.query.filter(Transaction.item_id == item.id)

            for transaction in transactions:
                receiver = User.query.filter_by(id=transaction.receiver_id).first()

                transaction_dict["transaction_id"] = transaction.id
                transaction_dict["receiver_name"] = receiver.username
                transaction_dict["receiver_points"] = receiver.givingPoints
                transaction_dict["receiver_num"] = receiver.contactNum
                transaction_dict['item_id'] = item.id
                transaction_dict["transaction_accepted"] = transaction.isAccepted
                transaction_dict["transaction_completed"] = transaction.isCompleted

                transaction_dict_copy = transaction_dict.copy()
                transaction_list.append(transaction_dict_copy )

    if request.method == "POST":
        transactionID = request.form.get('transactionID')
        receiverUsername = request.form.get('receiverUsername')
        itemID = request.form.get('itemID')

        accepted_transaction = Transaction.query.filter(Transaction.id == transactionID).first()
        accepted_transaction.isAccepted = True
        db.session.commit()

        app.logger.info('User gives item ' + str(itemID) + ' to ' + str(receiverUsername))

    return render_template('transactions.html', user=current_user, transaction_list = transaction_list)

@views.route('/receiver', methods=['GET', 'POST'])
def receiver():
    item_requests = [id[0] for id in Transaction.query.with_entities(Transaction.item_id).filter(Transaction.receiver_id == current_user.id)]
    item_completed = [id[0] for id in Transaction.query.with_entities(Transaction.item_id).filter(Transaction.isCompleted == True)]

    items = Item.query.filter(Item.user_id != current_user.id, Item.id.notin_(item_requests), Item.id.not_in(item_completed))
    if request.method == "POST":
        itemID = request.form.get('item')

        new_transaction = Transaction(item_id =itemID, receiver_id=current_user.id)
        db.session.add(new_transaction)
        db.session.commit()

        transactions=Transaction.query.all()
        for transaction in transactions:
            Items = Item.query.filter(Item.id == transaction.item_id).first()
            Receiver = User.query.filter(User.id == transaction.receiver_id).first()

        app.logger.info(current_user.username + " requested " + Items.itemName)

    return render_template('receiver.html', user=current_user, items=items)

@views.route('/requests', methods=['GET', 'POST'])
def requests():
    requests = Transaction.query.filter_by(receiver_id=current_user.id)
    item_list = []
    item_dict = {"item_id":"","item_name":"", "item_desc": "", "item_accepted": "", "transaction_id": "", "transaction_completed": ""}

    if requests: 
        for request_item in requests:
            item = Item.query.filter_by(id=request_item.item_id).first()
            print(request_item)
            item_dict["item_id"] = item.id
            item_dict["item_name"] = item.itemName
            item_dict["item_desc"] = item.itemDesc
            item_dict["item_accepted"] = request_item.isAccepted
            item_dict["transaction_id"] = request_item.id
            item_dict["transaction_completed"] = request_item.isCompleted
            print("Item Name: " + item.itemName + "\nItem Desc: " + item.itemDesc + "\nRequest Accepted: " + str(request_item.isAccepted) + "\nTransaction ID: " + str(request_item.id) + "\Transaction Completed: " + str(request_item.isCompleted))

            item_dict_copy = item_dict.copy()
            item_list.append(item_dict_copy )

    if request.method == "POST":
        transactionID = request.form.get('transactionID')
        itemID = request.form.get('itemID')

        completed_transaction = Transaction.query.filter(Transaction.id == transactionID).first()
        completed_transaction.isCompleted = True
        db.session.commit()

        giver_id = Item.query.filter(Item.id==itemID).first()
        giver = User.query.filter(User.id == giver_id.user_id).first()
        giver.givingPoints += 150
        db.session.commit()

        app.logger.info("Transaction "+ transactionID + " is completed. " + giver.username + " gains additional 150 giving points.")

    return render_template('requests.html', user=current_user, items=item_list)