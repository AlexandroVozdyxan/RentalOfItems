from functools import wraps
from flask import Flask, render_template, redirect, session, request
import sqlite3

from sqlalchemy import select
from sqlalchemy.sql.functions import current_user

from database import init_db, db_session
import models
from models import Feedback

app = Flask(__name__)
app.secret_key = 'FEh3487duH3&*#HS#d98H#d'


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return func(*args, **kwargs)
    return wrapper

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Db_open_close(object):
    def __init__(self, database):
        self.con = sqlite3.connect('db1.db')
        self.con.row_factory = dict_factory
        self.cur = self.con.cursor()
    def __enter__(self):
        return self.cur
    def __exit__(self, type, value, traceback):
        self.con.commit()
        self.con.close()

class DbHandler:
    db_file = "db1.db"

    def select(self, table_name, filter_dict=None):
        if filter_dict is None:
            filter_dict = {}
        with Db_open_close(self.db_file) as db_cur:
            query = f'SELECT * FROM {table_name}'
            if filter_dict:
                query += ' WHERE '
                itms = []
                for key, value in filter_dict.items():
                    itms.append(f'{key} = ?')
                query += ' AND '.join(itms)

                db_cur.execute(query, tuple(value for value in filter_dict.values()))
            else:
                db_cur.execute(query)
            result = db_cur.fetchall()
            print(f"Query: {query}")
            print(f"Result: {result}")
            return result

    def insert(self, table_name, data_dict):
        with Db_open_close(self.db_file) as db_cur:
            query = f'INSERT INTO {table_name} ( '
            query += ', '.join(data_dict.keys())
            query += ' ) VALUES ( '
            query += ', '.join([f':{itms}' for itms in data_dict.keys()])
            query += ' )'
            db_cur.execute(query, data_dict)

db_connector = DbHandler()

@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        init_db()
        query = select(models.User).where(models.User.login==username)
        user_data = db_session.execute(query).first()

        if user_data:

            session['user'] = user_data[0].login
            return 'Login successful, welcome  ' +  user_data[0].login
        else:
            return 'Wrong username or password', 401
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        form_data = dict(request.form)
        init_db()
        user = models.User(**form_data)
        db_session.add(user)
        db_session.commit()
        return redirect('/login')


@app.route('/logout', methods=['GET', 'POST', 'DELETE'])
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/profile', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@login_required
def profile():
   if request.method == 'GET':
       init_db()
       user_data = db_session.execute(select(models.User).filter_by(login=session['user'])).scalar()
       if user_data:
        return render_template("user.html", user=user_data)
       else:
           return "Wrong username or password", 401


   if request.method == 'PUT':
       return 'PUT'
   if request.method == 'PATCH':
       return 'PATCH'
   if request.method == 'DELETE':
       return 'DELETE'

@app.route('/profile/favorites', methods=['GET', 'POST', 'DELETE'])
def favorites():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'POST':
        return 'POST'
    if request.method == 'DELETE':
        return 'DELETE'

@app.route('/profile/favorites/<favorites_id>', methods=['GET', 'PUT', 'DELETE'])
def favorites_id(favorites_id):
    if request.method == 'GET':
        return 'GET'
    if request.method == 'PUT':
        return 'PUT'
    if request.method == 'DELETE':
        return 'DELETE'

@app.route('/profile/search_history', methods=['GET', 'DELETE'])
def search_history():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'DELETE':
        return 'DELETE'

@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        init_db()
        items_query = select(models.Item)
        items = list(db_session.execute(items_query).scalars())
        return render_template('items.html', items=items)

    if request.method == 'POST':
        if session.get('user') is None:
            return redirect('/login')
        else:
            init_db()

            current_user = db_session.scalar(select(models.User).where(models.User.login==session['user']))

            query_args = dict(request.form)
            query_args['owner'] = current_user.id
            new_item = models.Item(**query_args)

            db_session.add(new_item)
            db_session.commit()

        return redirect('/items')


@app.route('/items/<item_id>', methods=['GET', 'PUT', 'DELETE'])
def item(item_id):
    if request.method == 'GET':
        init_db()
        item_data = db_session.execute(select(models.Item).where(models.Item.id == item_id)).scalar()
        if item_data:
            return render_template('item.html', item=item_data, login=session['user'])
        else:
            return "Items not found", 404
    if request.method == 'DELETE':
        return 'DELETE'

@app.route('/leasers', methods=['GET'])
def leasers():
    if request.method == 'GET':
        init_db()
        leasers = db_session.execute(select(models.User)).scalars()
        return render_template('user.html', user=leasers)


@app.route('/leasers/<leaser_id>', methods=['GET'])
def leaser(leaser_id):
    if request.method == 'GET':
        init_db()
        leaser_id = db_session.execute(select(models.User).filter_by(id=leaser_id)).scalar()
        return 'GET'

@app.route('/contracts', methods=['GET', 'POST'])
@login_required
def contracts():
    if request.method == 'GET':
        init_db()
        contracts = db_session.execute(select(models.Contract)).scalars()
        return render_template('contract.html', contracts=contracts)
    if request.method == 'POST':
        init_db()
        contract = models.Contract(**request.form)
        contract.leaser = session['user']
        db_session.add(contract)
        db_session.commit()
        return redirect('/')

@app.route('/contracts/<contract_id>', methods=['GET', 'PUT', 'PATCH'])
def contracts_id(contract_id):
    if request.method == 'GET':
        init_db()
        contract = db_session.execute(select(models.Contract).filter_by(id=contract_id)).scalar()
        return render_template('contract.html', contract=contract)
    if request.method == 'PUT':
        return f'PUT: {contract_id}'
    if request.method == 'PATCH':
        return f'PATCH: {contract_id}'

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'POST':
        return 'POST'

@app.route('/complaints', methods=['GET', 'POST'])
def complaints():
    if request.method == 'POST':
        init_db()
        complaints = Feedback(**request.form)
        db_session.add(complaints)
        db_session.commit()
        return redirect('/')


@app.route('/compare', methods=['GET', 'PUT'])
def compare():
    if request.method == 'GET':
        init_db()
        item1 = db_session.execute(select(models.Item)).scalar()
        item2 = db_session.execute(select(models.Item)).scalar()
        return render_template('compare.html', item1=item1, item2=item2)
    if request.method == 'PUT':
        return 'PUT'

if __name__ == '__main__':
    app.run()