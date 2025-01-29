from functools import wraps

from flask import Flask, render_template, redirect, session
from flask import request
import sqlite3

from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'FEh3487duH3&*#HS#d98H#d'
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


def login_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return func(*args, **kwargs)
    return wrapped
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with Db_open_close('db1.db') as db_cur:
            db_cur.execute('''SELECT id, full_name FROM user WHERE login = ? AND password = ?''',
                           (username, password))
            user = db_cur.fetchone()
            if user:
                session['user_id'] = user['id']
                session['full_na,e'] = user['full_name']
                return 'Logged in successfully!'
            else:
                return 'Invalid username or password!', 401
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        with Db_open_close('db1.db') as db_cur:
            form_data = request.form
            db_cur.execute('''INSERT INTO user
            (login, password, ipn, full_name, contacts, photo, passport)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                           (form_data['login'], form_data['password'], form_data['ipn'], form_data['full_name'],
                           form_data['contacts'], form_data['photo'], form_data['passport']
                           ))

        return redirect('/login')

@app.route('/logout', methods=['GET', 'POST', 'DELETE'])
@login_required
def logout():
    session.pop('user_id', None)
    return redirect('/login')

@app.route('/profile', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@login_required
def profile():
    if session.get('user_id') is None:
        return redirect('/login')
    if request.method == 'GET':
        with Db_open_close('db1.db') as db_cur:
            query = '''SELECT full_name FROM user WHERE login = ?'''
            db_cur.execute(query, (session['user_id'],))
            full_name = db_cur.fetchone()['full_name']
        return render_template('user.html', full_name=full_name)
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
        with Db_open_close('db1.db') as db_cur:
            db_cur.execute("SELECT * FROM item")
            items = db_cur.fetchall()
        return render_template('items.html', items=items)
    if request.method == 'POST':
        if session.get('user_id') is None:
            return redirect('/login')
        with Db_open_close('db1.db') as db_cur:

            user_login = session['user_id']
            db_cur.execute("select id from user where login = ?", (user_login,))
            user_id = db_cur.fetchone()['id']

            query_args = dict(request.form)
            query_args['owner'] = user_id

            db_cur.execute('''INSERT INTO item (photo, name, description, price_hour, price_day, price_week, price_month, owner)
            VALUES (:photo, :name, :description, :price_hour, :price_day, :price_week, :price_month, :owner)''', query_args)
        return redirect('/items')

@app.route('/items/<item_id>', methods=['GET', 'PUT', 'DELETE'])
def item(item_id):
    if request.method == 'GET':
        return render_template('oneitemform.html', item_id=item_id)
    if request.method == 'PUT':
        return f'PUT {item_id}'
    if request.method == 'DELETE':
        if session.get('user_id') is None:
            return redirect('/login')
        return f'DELETE {item_id}'

@app.route('/leasers', methods=['GET'])
def leasers():
    if request.method == 'GET':
        return 'GET'

@app.route('/leasers/<leaser_id>', methods=['GET'])
def leaser(leaser_id):
    if request.method == 'GET':
        return f'GET: {leaser_id}'

@app.route('/contracts', methods=['GET', 'POST'])
@login_required
def contracts():
    if request.method == 'GET':
        with Db_open_close('db1.db') as db_cur:
            db_cur.execute("SELECT * FROM contract")
            contracts = db_cur.fetchall()
        return render_template('contracts.html', contracts=contracts)
        return 'GET'
    if request.method == 'POST':
        with Db_open_close('db1.db') as db_cur:
            db_cur.execute("select id from user where login = ?", (session['user_id'],))
            my_id = db_cur.fetchone()['id']
            taker_id = my_id
            item_id = request.form['item']
            # 1
            leaser_id = request.form['leaser']
            # 2
            db_cur.execute("select * from item where id = ?", (item_id,))
            leaser_id = db_cur.fetchone()['owner']

            contract_status = 'pending'

            query_args = (request.form['text'], request.form['start_day'], request.form['end_day'], leaser_id, taker_id, item_id, contract_status)
            inser_query = '''insert into contcract (text, start_day, end_day, leaser, taker, item, status) values (/, ?, ?, ?, ?, ?, ?)'''
            db_cur.execute(inser_query, query_args)

        return 'POST'

@app.route('/contracts/<contract_id>', methods=['GET', 'PUT', 'PATCH'])
def contracts_id(contract_id):
    if request.method == 'GET':
        return f'GET: {contract_id}'
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
    if request.method == 'GET':
        return render_template('feedback.html')
    if request.method == 'POST':
        with Db_open_close('db1.db') as db_cur:
            form_data = request.form
            db_cur.execute('''INSERT INTO feedback
            (author, user, text, grade, contract)
            VALUES (?, ?, ?, ?, ?)''',
            (form_data['author'], form_data['user'],
             form_data['text'], form_data['grade'],
             form_data['contract'])
                           )
        return render_template('complain_sub.html')

@app.route('/complaints/<complaint_id>', methods=['GET', 'PUT', 'DELETE'])
def complaints_id(complaint_id):
    if request.method == 'GET':
        return f'GET: {complaint_id}'
    if request.method == 'PUT':
        return f'PUT: {complaint_id}'
    if request.method == 'DELETE':
        return f'DELETE: {complaint_id}'

@app.route('/compare', methods=['GET', 'PUT'])
def compare():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'PUT':
        return 'PUT'

if __name__ == '__main__':
    app.run()
