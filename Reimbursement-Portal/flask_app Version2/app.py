from flask import Flask,render_template, request,redirect,url_for,session,flash,Response,send_from_directory
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import re
import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    handler=RotatingFileHandler('reimbursement_portal.log',maxBytes=1000000,backupCount=5)
    handler.setLevel(logging.INFO)
    formatter=logging.Formatter('%(asctime)s - %(name)s -%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    

app=Flask(__name__)
#create an instance of the Flask class,

app.secret_key = 'reimbursement'  
# Required for session management

#Configuring the MYSQL Connection server 
app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''

mysql = MySQL(app)
#Connecting Flask application to MYSQL database


setup_logging(app)

@app.before_request
def log_request_info():
    app.logger.info('Request Method : %s',request.method)

@app.after_request
def log_response_info(response):
    app.logger.info('Response Status: %s',response.status)
    return response

@app.errorhandler(404)
def page_not_found(e):
    app.logger.error('Page not found: %s',request.path)
    return 'This page does not exist',404


# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename[2:-1])


@app.route('/',methods=['POST','GET'])
def login():
    app.logger.info("Login Page accessed")
    msg=''
    if request.method=='POST': 
        email_id=request.form['email_id']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email_id =%s AND password=%s',(email_id,password))
        account=cursor.fetchone()
        if account:
            msg='Logged in successfully'
            print("successful")
            user_id = account[0]
            user_name = account[1]
            cursor.execute('SELECT user_id FROM users WHERE email_id=%s and password=%s',(email_id,password))
            user_id=cursor.fetchone()[0]
            cursor.execute('SELECT username FROM users WHERE email_id=%s and password=%s',(email_id,password))
            user_name=cursor.fetchone()
            employee_type = account[5]
            if employee_type =='manager':
                cursor.execute('SELECT * FROM requests WHERE handled_by=%s',(user_id,))
                data=cursor.fetchall()
                cursor.execute('SELECT * FROM requests WHERE user_id=%s',(user_id,))
                manager_data=cursor.fetchall()
                session['manager_id']=user_id
                session['user_id']=user_id
                return render_template('manager-page.html',manager_id=user_id,manager_name=user_name[0],data=data,manager_data=manager_data,user_id=user_id)
            else:
                cursor.execute('SELECT * FROM requests WHERE user_id=%s',(user_id,))
                data=cursor.fetchall()
                session['user_id']=user_id
                user_id=session.get('user_id')
                return render_template('employee-page.html',user_id=user_id,user_name=user_name,data=data)
        else:
            msg='The email address or the password is incorrect.Try Again.'
            print("failed")
            return render_template('login.html',msg=msg)
    else:
        return render_template('login.html')

 
@app.route('/register', methods = ['POST', 'GET'])
def register():
    app.logger.info("Employee Registration Page accessed")
    msg='' 
    if request.method == 'POST':
        username = request.form['username']
        email_id = request.form['email_id']
        password = request.form['password']
        department = request.form['department']
        employee_type=request.form['employee_type']

        if not re.match(".*@nucleusteq.com",email_id):
            msg = "Please enter a valid company email address only"
            return render_template('register.html', msg=msg)
        else:
        #Creating a connection cursor
            cursor = mysql.connection.cursor()
            cursor.execute('''INSERT INTO users (username, email_id, password, department,employee_type) VALUES (%s, %s, %s, %s,%s)''', (username, email_id, password, department,employee_type))

        #Saving the Actions performed on the DB
            mysql.connection.commit()

        #Closing the cursor
            cursor.close()
            msg="You have successfully registered"
            return render_template('login.html',msg=msg)
    
    else:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM department')
        departments=cursor.fetchall()
        return render_template('register.html',departments=departments)


@app.route('/admin_login',methods=['POST','GET'])
def admin_login():
    app.logger.info("Admin Login Page Accessed")
    msg=''
    admin_name=''
    if request.method=='POST':
        email_id=request.form['email_id']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT * FROM admin WHERE email_id =%s AND password=%s',(email_id,password,))
        account=cursor.fetchone()
        if account:
            admin_name = account[1]
            admin_id = account[0]
            session['admin_name'] = admin_name
            session['admin_id'] = admin_id
            return redirect(url_for('admin_dashboard',admin_name=admin_name,admin_id=admin_id))
        else:

            msg='Incorrect username or password! Admin access denied'
            return render_template('admin-login.html',msg=msg)
    return render_template('admin-login.html')



@app.route('/employee_page',methods=['POST','GET'])
def employee_page():
    user_id=session.get('user_id')
    user_name=session.get('user_name')

    if request.method=='POST':
        app.logger.info("Reimbursement Request Page Accessed")
        return render_template('new-request.html',user_id=user_id)
    else:
        app.logger.info("Employee Page Accessed")
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT * FROM requests WHERE user_id=%s',(user_id,))
        data=cursor.fetchall()
        return render_template('employee-page.html',data=data,user_id=user_id,user_name=user_name)
    

@app.route('/new_request',methods=['POST','GET'])
def new_request():
    msg=''
    msg2=''
    cursor = mysql.connection.cursor()
    user_id=session.get('user_id')
    if request.method=='POST':
        user_id=request.form['user_id']
        expense_type = request.form['expense_type']
        amount = request.form['amount']
        date = request.form['date']
        receipt = request.files['receipt']

        if not receipt or not allowed_file(receipt.filename):
            msg2= "Receipt is required and must be a valid image file"
            return render_template('new-request.html', user_id=user_id, msg2=msg2)

        filename = secure_filename(receipt.filename)
        receipt_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)
        receipt.save(receipt_path)
        app.logger.info("Reimbursement Request Submitted")
        
        cursor.execute('''INSERT INTO requests (user_id,expense_type, amount, date, receipt) VALUES (%s, %s, %s, %s,%s)''', (user_id,expense_type, amount, date, filename))
   #Saving the Actions performed on the DB
        mysql.connection.commit()

        cursor.execute('SELECT request_id FROM requests WHERE user_id=%s AND expense_type=%s AND amount=%s AND date=%s', (user_id, expense_type, amount, date))
        request_id = cursor.fetchone()

        cursor.execute('''INSERT INTO audittrail (timestamp,request_id,user_id,event_type, event_description) VALUES (NOW(),%s, %s, 'SUBMISSION','The reimbursement Request has been submitted')''', (request_id,user_id))

        #Saving the Actions performed on the DB
        mysql.connection.commit()

        cursor.execute('SELECT * FROM users WHERE user_id=%s',(user_id,))
        employee=cursor.fetchone()
        employee_type=employee[5]

        if employee_type=='manager':
                cursor.execute('SELECT * FROM requests WHERE handled_by=%s',(user_id,))
                data=cursor.fetchall()
                cursor.execute('SELECT * FROM requests WHERE user_id=%s',(user_id,))
                manager_data=cursor.fetchall()
                return render_template('manager-page.html',manager_data=manager_data,data=data)
        else:
                cursor.execute('SELECT username from users Where user_id=%s',(user_id,))
                user_name=cursor.fetchone()
                cursor.execute('SELECT * FROM requests WHERE user_id=%s',(user_id,))
                data=cursor.fetchall()
                return render_template('employee-page.html',user_name=user_name,data=data)
    else:
        user_id=session.get('user_id')
        return render_template('new-request.html',user_id=user_id)


  

@app.route('/manager_page',methods=['POST','GET'])
def manager_page():
    cursor=mysql.connection.cursor()
    manager_id=request.form['manager_id']
    if request.method=='POST':
        manager_id=request.form['manager_id']
        request_id=request.form['request_id']
        status=request.form['status']
        comment=request.form['comment']
        cursor.execute('UPDATE requests SET status=%s,comments=%s WHERE request_id=%s',(status,comment,request_id,))
        mysql.connection.commit()

        cursor.execute('''INSERT INTO audittrail (timestamp,request_id,user_id,event_type, event_description) VALUES (NOW(),%s, %s, 'REVIWED','Manager has reviewed the reimbursement request')''', (request_id,manager_id))
        mysql.connection.commit()

        cursor.execute('SELECT * FROM requests WHERE handled_by=%s',(manager_id,))
        data=cursor.fetchall()
        cursor.execute('SELECT * FROM requests WHERE user_id=%s',(manager_id,))
        manager_data=cursor.fetchall()
        app.logger.info("Manager Approved/Declined Reimbursement Request")
        return render_template('manager-page.html',data=data,manager_data=manager_data)
    else:
        app.logger.info("Manager Page Accessed")
        manager_id=session.get('manager_id')
        cursor.execute('SELECT * FROM requests WHERE handled_by=%s',(manager_id,))
        data=cursor.fetchall()
        cursor.execute('SELECT * FROM requests WHERE user_id=%s',(manager_id,))
        manager_data=cursor.fetchall()
        return render_template('manager-page.html',manager_data=manager_data,data=data)
       

@app.route('/admin_dashboard',methods=['GET','POST'])
def admin_dashboard():
        app.logger.info("Admin Dashboard Page Accessed")
        admin_name = session.get('admin_name')
        admin_id = session.get('admin_id')
        cursor=mysql.connection.cursor()
        
        if request.method=='POST':
            request_id=request.form['request_id']
            status=request.form['status']
            comments=request.form['comments']
            cursor.execute('UPDATE requests SET status=%s,comments=%s WHERE request_id=%s',(status,comments,request_id,))
            mysql.connection.commit()
            cursor.execute('''INSERT INTO audittrail (timestamp,request_id,user_id,event_type, event_description) VALUES (NOW(),%s, %s, 'REVIWED','Admin has reviewed the reimbursement request')''', (request_id,admin_id))
            mysql.connection.commit()
            app.logger.info("Admin Changed Status of Reimbursement Request")
               
        cursor.execute('select * from requests')
        data=cursor.fetchall()
        return render_template('admin-dashboard.html',admin_name=admin_name,data=data)


@app.route('/admin_assign',methods=['GET','POST'])
def admin_assign():
    if request.method=='POST':
        employee_id=request.form['employee_id']
        department=request.form['department']
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE employee_type='manager' and department=%s ",(department,))
        dept_managers=cursor.fetchall()

        cursor.execute("SELECT * FROM users WHERE employee_type='employee' and assigned_to='admin' ")
        employees=cursor.fetchall()

        cursor.execute("SELECT * FROM users WHERE employee_type='manager' and assigned_to='admin' ")
        managers=cursor.fetchall()

        return render_template('admin-assign.html',dept_managers=dept_managers,employees=employees,managers=managers,department=department,employee_id=employee_id)
        
    else:
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE employee_type='manager' and assigned_to='admin' ")
        managers=cursor.fetchall()
        cursor.execute("SELECT * FROM users WHERE employee_type='employee' and assigned_to='admin' ")
        employees=cursor.fetchall()
        return render_template('admin-assign.html',managers=managers,employees=employees)
    
    
@app.route('/admin_assign_submit', methods=['POST'])
def admin_assign_submit():
    employee_id=request.form['employee_id']
    manager_id=request.form['manager_id']
    cursor=mysql.connection.cursor()
    cursor.execute('UPDATE users SET assigned_to=%s WHERE user_id=%s',(manager_id,employee_id))
    mysql.connection.commit()
    cursor.execute('UPDATE requests SET handled_by=%s WHERE user_id=%s',(manager_id,employee_id))
    mysql.connection.commit()

    
    cursor.execute("SELECT * FROM users WHERE employee_type='manager' and assigned_to='admin' ")
    managers=cursor.fetchall()
    cursor.execute("SELECT * FROM users WHERE employee_type='employee' and assigned_to='admin' ")
    employees=cursor.fetchall()
    cursor.execute('SELECT request_id FROM requests where user_id=%s',(employee_id,))
    results=cursor.fetchall()
    admin_id = session.get('admin_id')

    for result in results:
        request_id=result[0]
        cursor.execute('''INSERT INTO audittrail (timestamp,request_id,user_id,event_type, event_description) VALUES (NOW(),%s, %s, 'ASSIGNED','Admin has assigned the reimbursement request to manager')''', (request_id,admin_id))
    mysql.connection.commit()
    return render_template('admin-assign.html',managers=managers,employees=employees)




@app.route('/admin_deleteDept',methods=['POST','GET'])
def admin_deleteDept():
    app.logger.info("Delete Department Page Accessed")
    cursor=mysql.connection.cursor()
    if request.method=='POST':
        department_id=request.form['department_id']
        if department_id:
            cursor.execute('DELETE FROM department WHERE department_id=%s',(department_id,))
            mysql.connection.commit()
            app.logger.info("Admin Deleted Department")

    cursor.execute('SELECT * FROM department')
    departments=cursor.fetchall()
    return render_template('admin-deleteDept.html',departments=departments)
    
    
@app.route('/admin_insertDept',methods=['POST','GET'])
def admin_insertDept():
        app.logger.info("Insert Department Page Accessed")
        msg=''
        if request.method=='POST':
            department_name=request.form['department_name']
            cursor=mysql.connection.cursor()
            cursor.execute('INSERT INTO department(department_name) VALUES(%s)',(department_name,))
            mysql.connection.commit()
            msg='Department has been successfully inserted'
            app.logger.info("Admin Inserted Department")
            return render_template('admin-insertDept.html',msg=msg)
        else:
            return render_template('admin-insertDept.html')


@app.route('/admin_deleteEmp',methods=['POST','GET'])
def admin_deleteEmp():
    app.logger.info("Delete Employee Page Accessed")
    cursor=mysql.connection.cursor()
    if request.method=='POST':
        user_id=request.form['user_id']
        cursor.execute('DELETE FROM users WHERE user_id=%s',(user_id,))
        mysql.connection.commit()
        cursor.execute('SELECT * FROM users')
        users=cursor.fetchall()
        app.logger.info("Admin Deleted Employee/Manager")
        return render_template('admin-deleteEmp.html',users=users)
    else:
        cursor.execute('SELECT * FROM users')
        users=cursor.fetchall()
        return render_template('admin-deleteEmp.html',users=users)




@app.route('/admin_audittrail',methods=['GET'])
def admin_audittrail():
    app.logger.info("Audit Trail Page Accessed")
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM audittrail')
    table=cursor.fetchall()
    return render_template('admin-audittrail.html',table=table)



if __name__ == '__main__': 
    app.run(debug=True)





