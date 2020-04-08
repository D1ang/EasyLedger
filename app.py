import os
import json
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson import json_util


from os import path
if path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = 'database'
app.config["MONGO_URI"] = os.environ.get('MONGO_URI')


mongo = PyMongo(app)


@app.route("/")
@app.route('/get_dashboard')
def get_dashboard():
    return render_template("dashboard.html")


"""Creates the route to the add transaction page and creates a find for the catagories list"""
@app.route('/get_transactions')
def get_transactions():
    return render_template('transactions.html',
                           transactions=mongo.db.transactions.find(),
                           categories=mongo.db.categories.find())
    # transactions = mongo.db.transactions.find({"catagory":"Household"}))


"""Creates a transaction to the database after the button is pressed"""
@app.route('/insert_transaction', methods=['POST'])
def insert_transaction():
    transactions = mongo.db.transactions
    transactions.insert_one(request.form.to_dict())
    return redirect(url_for('get_transactions'))


@app.route('/edit_transaction/<transaction_id>')
def edit_transaction(transaction_id):
    the_transaction = mongo.db.transactions.find_one(
        {"_id": ObjectId(transaction_id)})
    all_categories = mongo.db.categories.find()
    return render_template('edittransaction.html', transaction=the_transaction, categories=all_categories)


@app.route('/update_transaction/<transaction_id>', methods=['POST'])
def update_transaction(transaction_id):
    transactions = mongo.db.transactions
    transactions.update({'_id': ObjectId(transaction_id)},
                        {
        'transition': request.form.get('transition'),
        'category_name': request.form.get('category_name'),
        'details': request.form.get('details'),
        'date': request.form.get('date'),
        'amount': request.form.get('amount')
    })
    return redirect(url_for('get_transactions'))


"""Deletes a transaction by searching on it's id"""
@app.route('/delete_transaction/<transaction_id>')
def delete_transaction(transaction_id):
    mongo.db.transactions.remove({'_id': ObjectId(transaction_id)})
    return redirect(url_for('get_transactions'))


"""Searches for transactions on Mongo when the route is selected then appensd the transactions en convert them to JSON"""
@app.route("/transactions/json")
def transactionsJSON():
    transactions = mongo.db.transactions.find()
    json_transactions = []
    for transaction in transactions:
        json_transactions.append(transaction)
    json_transactions = json.dumps(
        json_transactions, default=json_util.default)
    return json_transactions


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
