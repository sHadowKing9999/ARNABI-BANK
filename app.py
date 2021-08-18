import pymysql
from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import time
import datetime
import MySQLdb.cursors
import re

app = Flask(__name__)
sender=""
app.secret_key = 'Warrior320'



app.config['MYSQL_HOST'] = 'sql6.freemysqlhosting.net'
app.config['MYSQL_USER'] = 'sql6431161'
app.config['MYSQL_PASSWORD'] = 'Ipjnywh1jV'
app.config['MYSQL_DB'] = 'sql6431161'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
ts = time.time()
timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

# @app.route('/')
# def init():
#     cursor=mysql.connection.cursor()
#     cursor.execute('''CREATE DATABASE IF NOT EXISTS BANK DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
# ''')
#     return 'done'
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/customers')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM customers")

    data1 = cursor.fetchall()

    return render_template('customers.html', data=data1)


@app.route('/transaction', methods=['GET', 'POST'])
def make():
    msg = 'Please enter details to be added'
    if request.method == 'POST' and 'cid' in request.form and 'cname' in request.form and 'cemail' in request.form and 'cbal' in request.form:
        user = request.form['cname']
        id = request.form['cid']
        email = request.form['cemail']
        bal = request.form['cbal']
        return render_template('make.html',value1=user,value2=id,value3=email,value4=bal,form={'amount':'','reciever':''})



@app.route("/transactions", methods=['GET', 'POST'])
def transact():
    if request.method == 'POST' and 'reciever' in request.form and 'amount' in request.form and 'pname' in request.form and 'pbal' in request.form:
        global sender
        sender=request.form['id']
        reciever = request.form['reciever']
        amount=request.form['amount']
        amount1=request.form['amount']
        formEr={"reciever":[],"amount":[]}
        error=False
        if sender==reciever:
            formEr['reciever'].append("Sender and Receiver cannot be same")
            error=True
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT curr_bal FROM customers WHERE id=%s", (reciever,))
        if not cursor.fetchone():
            formEr['reciever'].append("Receiver with given account number not found")
            error=True
        if  not amount.isnumeric():
            formEr['amount'].append("Invalid Input")
            error=True
        
        if error:
            return render_template("make.html",form=formEr,value1=request.form['pname'],value2=request.form['id'],value3=request.form['email'],value4=request.form['pbal'])

        amount = float(amount)
        amount1 = float(amount1)
        scurrbal = float(request.form['pbal'])
        
        sbal = scurrbal - amount
        cursor.execute("SELECT curr_bal FROM customers WHERE id=%s", (reciever,))
        rcurr_bal = cursor.fetchone()
        rcurrbal = float(rcurr_bal[0])
        rbal = rcurrbal + amount1
        sname=request.form['pname']
        cursor.execute("SELECT name from customers where id=%s", (reciever,))
        rname=cursor.fetchone()[0]
        if scurrbal >= amount:
            cursor.execute("UPDATE customers SET curr_bal=%s where id=%s", (rbal, reciever,))
            cursor.execute("UPDATE customers SET curr_bal=%s where id=%s", (sbal, sender,))
            cursor.execute("INSERT INTO transactions(sname,rname,amount,sid,rid) VALUES ( %s, %s,%s,%s,%s)",
                           (sname, rname, amount,sender,reciever,))
            mysql.connection.commit()
        else:
            return render_template("failure.html",sender=sender,sname=sname,rname=rname,receiver=reciever,amount=amount)
        return render_template("success.html",transaction='/history',sender=sender,receiver=reciever,sname=sname,rname=rname,sbal=scurrbal,rbal=rbal,amount=amount)
        # return render_template('transact.html',value=tid)


@app.route('/history')
def transhis():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM transactions ORDER BY time DESC')
    data1 = cursor.fetchall()
    return render_template('transaction.html', data=data1)

if __name__ == "__main__":
    app.run(debug=True)
