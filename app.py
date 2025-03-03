from functools import wraps

from flask import Flask, render_template, redirect, session
from flask import request
import sqlite3

from sqlalchemy import select, update

import celery_tasks
import database
import model

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
        self.con = sqlite3.connect('db1_.db')
        self.con.row_factory = dict_factory
        self.cur = self.con.cursor()
    def __enter__(self):
        return self.cur
    def __exit__(self, type, value, traceback):
        self.con.commit()
        self.con.close()

class DbHandler:
    db_file = "db1_.db"

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
            query += ','.join(data_dict.keys())
            query += ' ) VALUES ( '
            query += ','.join([f':{itms}' for itms in data_dict.keys()])
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

        database.init_db()
        user_data = database.db_session.execute(
            select(model.User).filter_by(login=username, password=password)
        ).scalar()
        if user_data:
            session['user'] = user_data.user_id
            return redirect('/profile')
        else:
            return render_template('login.html', error='Invalid username or password')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        form_data = dict(request.form)
        database.init_db()
        user = model.User(**form_data)
        database.db_session.add(user)
        database.db_session.commit()
        return redirect('/login')

@app.route('/logout', methods=['GET', 'POST', 'DELETE'])
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/profile', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@login_required
def profile():
    database.init_db()
    if session.get('user') is None:
        return redirect('/login')
    if request.method == 'GET':
        user_data = database.db_session.execute(
            select(model.User).filter_by(user_id=session['user'])).scalar()
        return render_template('user.html', user=user_data)
    if request.method == 'POST':
        database.init_db()
        user = database.db_session.execute(update(model.User).filter_by(user=session['user']).values(**request.form))
        database.db_session.commit()
        database.db_session.close()
        return redirect('/user')
    if request.method == 'DELETE':
        user = database.db_session.execute(select('user').filter_by(
            user_id=session['user'])).scalar()
        database.db_session.delete(user)
        database.db_session.commit()
        session.pop('user', None)
        session.pop(user, None)
        return redirect('/login')



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
        database.init_db()
        item_data = select(model.Item)
        item_data = database.db_session.execute(select(model.Item)).scalar()
        return render_template('items.html', items=item_data)

    if request.method == 'POST':
        if session.get('user') is None:
            return redirect('/login')

        database.init_db()
        item = model.Item(**request.form)
        item.owner = session['user']

        database.db_session.add(item)
        database.db_session.commit()

        return redirect('/items')


@app.route('/items/<item_id>', methods=['GET', 'PUT', 'DELETE'])
def item(item_id):
    if request.method == 'GET':
        if session.get('user') is None:
            return redirect('/login')
        database.init_db()
        item = database.db_session.execute(select(model.Item).filter_by(id=item_id)).scalar()
        return render_template('item.html', item=item, user_id=session['user'])

@app.route('/items/<int:item_id>/delete', methods=['DELETE'])
@login_required
def item_delete(item_id):
    database.init_db()
    item = database.db_session.get(model.Item, id=item_id)
    if item and session.get('user') == item.owner:
        database.db_session.delete(item)
        database.db_session.commit()
        return render_template('/')
    return redirect('User not in session or not found such item')

@app.route('/leasers', methods=['GET'])
def leasers():
    if request.method == 'GET':
        with Db_open_close('db1_.db') as db_cur:
            db_connector.select('leaser')
            leaser_data = db_cur.fetchall()
            return render_template('user.html', user=leaser_data)


@app.route('/leasers/<leaser_id>', methods=['GET'])
def leaser(leaser_id):
    if request.method == 'GET':
        with Db_open_close('db1_.db') as db_cur:
            db_connector.select('leaser', {'leaser_id': leaser_id})
        return 'GET'

@app.route('/contracts', methods=['GET', 'POST'])
@login_required
def contracts():
    if request.method == 'GET':
        database.init_db()
        contracts = database.db_session.execute(select(model.Contract)).scalar().all
        leaser = database.db_session.execute(select(model.User).filter_by(
            user_id=model.Contract.leaser)).scalar()
        taker = database.db_session.execute(select(model.User).filter_by(
            user_id=model.Contract.taker)).scalar()
        item = database.db_session.execute(select(model.Item).filter_by(
            id=model.Contract.item)).scalar()
        return render_template('contract.html', contracts=contracts, leaser=leaser, taker=taker, item=item)
    if request.method == 'POST':
        contract = model.Contract(**request.form)
        contract.leaser = session['user']
        database.db_session.add(contract)
        database.db_session.commit()
        celery_tasks.send_email(contract.id)
        return redirect('/')


@app.route('/contracts/<int:contract_id>', methods=['GET'])
@login_required
def contracts_id(contract_id):
    if request.method == 'GET':
        database.init_db()
        if session.get('user') is None:
            return redirect('/login')
        contract = database.db_session.execute(
            select(model.Contract).filter_by(
                id=contract_id)).scalar()
        name1 = database.db_session.execute(select(model.User).filter_by(user_id=contract.leaser)).scalar()
        name2 = database.db_session.execute(select(model.User).filter_by(user_id=contract.taker)).scalar()
        item = database.db_session.execute(select(model.Item).filter_by(id=contract.item)).scalar()
        return render_template('contract.html', contract=contract, name1=name1, name2=name2, item=item)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'POST':
        return 'POST'

@app.route('/complaints', methods=['GET', 'POST'])
def complaints():
    if request.method == 'POST':
        with Db_open_close('db1_.db') as db_cur:
            form_data = request.form
            db_connector.insert('feedback', form_data)

            return redirect('/')


@app.route('/compare', methods=['GET', 'PUT'])
def compare():
    if request.method == 'GET':
        item1_id = request.args.get('item1')
        item2_id = request.args.get('item2')
        if item1_id and item2_id:
            item1 = db_connector.select('item', {'id': item1_id})
            item2 = db_connector.select('item', {'id': item2_id})
            if item1 and item2:
                return render_template('compare.html', item=item1[0], item2=item2[0])
        return "Items not found", 404
    if request.method == 'PUT':
        return 'PUT'


@app.route('/add_task', methods=['GET'])
def set_task():
    celery_tasks.add.delay(1, 2)
    return "Task sent"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")