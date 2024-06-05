import pytest
from flask import session,send_from_directory
from app import app
from io import BytesIO
import os
from werkzeug.utils import secure_filename
import logging
import re

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_admin_login_successful(client):
    response=client.post('/admin_login',data={'email_id':'rajesh.sahu@nucleusteq.com','password':'rajesh123'})
    assert response.status_code==302
    assert '/admin_dashboard' in response.location

def test_admin_login_unsuccessful(client):
    response=client.post('/admin_login',data={'email_id':'riya.sharam@nucleusteq.com','password':'riya123'})
    assert response.status_code==200
    assert b'Incorrect username or password! Admin access denied' in response.data


def test_login_successful_manager(client):
    response=client.post('/',data={'email_id':'riya.sharma@nucleusteq.com','password':'riya123'})
    assert response.status_code==200

def test_login_successful_employee(client):
    response=client.post('/',data={'email_id':'shreya.gupta@nucleusteq.com','password':'shreya1'})
    assert response.status_code==200

def test_login_unsuccessful(client):
    response=client.post('/',data={'email_id':'abc.xyz@nucleusteq.com','password':'123'})
    assert response.status_code==200
    assert b'The email address or the password is incorrect.Try Again.' in response.data

def test_get_register_page(client):
    response=client.get('/register')
    assert response.status_code==200

def test_get_loginpage(client):
    response=client.get('/')
    assert response.status_code==200
    
def test_register(client):
    response=client.post('/register',data={'email_id':'yashi.sahu@nucleusteq.com','password':'123',
                                           'username':'Yashi Sahu','department':'Marketing','employee_type':'manager'})
    assert response.status_code==200
    assert b'You have successfully registered' in response.data

def test_register_invalid_email_address(client):
    response=client.post('/register',data={'email_id':'yashisahu30@gmail.com','password':'abc',
                                           'username':'Yashi','department':'Marketing','employee_type':'manager'})
    assert response.status_code==200
    assert b'Please enter a valid company email address only' in response.data


def test_get_admin_login_page(client):
    response=client.get('/admin_login')
    assert response.status_code==200
    

def test_admin_login_successful(client):
    response=client.post('/admin_login',data={'email_id':'rajesh.sahu@nucleusteq.com','password':'rajesh123'})
    assert response.status_code==302
    assert '/admin_dashboard' in response.location


def test_employee_page_logged_in(client):
    # Set up the session
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id']=13
        sess['email_id']='shreya.gupta@nucleusteq.com'
        sess['password']='shreya1'
        sess['user_name']='Shreya'
    response = client.get('/employee_page')
    assert response.status_code == 200

def test_employee_page_post_redirect_request_page(client):
    # Set up the session
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id']=13
        sess['email_id']='shreya.gupta@nucleusteq.com'
        sess['password']='shreya1'
        sess['user_name']='Shreya'
    response = client.post('/employee_page')
    assert response.status_code == 200
   

def test_employee_page_is_logged_in(client):
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id']=13
    response = client.get('/employee_page')
    assert response.status_code == 200
    

def test_get_new_request_page(client):
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = 13
    response=client.get('/new_request')
    assert response.status_code==200

def test_submit_request_without_valid_receipt(client):
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = 13
    data = {
        'user_id': '13',
        'amount': '200',
        'expense_type': 'Travelling',
        'date': '2024-05-02',
        'employee_type': 'employee',
        'receipt': (BytesIO(b'file content'), 'abc.txt') 
    }
    response = client.post('/new_request', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b'Receipt is required and must be a valid image file' in response.data



def test_submit_request_employee_logged_in(client):
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = 13
    response = client.post('/new_request', data={'user_id':'13','amount': '200','expense_type':'Travelling',
                                                 'date':'2024-05-02','employee_type':'employee','receipt': (BytesIO(b'file content'), 'abc.jpg') })
    assert response.status_code == 200


def test_submit_request_manager_logged_in(client):
    # Set up the session
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = '11'
    response = client.post('/new_request', data={'user_id':'11','amount': '200','expense_type':'Travelling','date':'2024-05-02','employee_type':'manager',
                                                 'receipt': (BytesIO(b'file content'), 'abc.jpg')})
    assert response.status_code == 200
      


def test_submit_request_not_logged_in(client):
    response = client.post('/new_request', data={'amount': '150'}, follow_redirects=False)
    assert response.status_code == 400
    


def test_request_page_amount_greater_Travelling(client):
    # Set up the session
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = 1
        sess['expense_type'] = 'Travelling'
        sess['amount'] = 20000
    response = client.get('/new_request')
    assert response.status_code == 200
    assert b'You cannot claim amount greater than Rs.15000 for Travelling' in response.data


def test_request_page_amount_greater_Relocation(client):
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = 1
        sess['expense_type'] = 'Relocation'
        sess['amount'] = 21000

    response = client.get('/new_request')
    assert response.status_code == 200
    assert b'You cannot claim amount greater than Rs.20000 for Relocation' in response.data


def test_request_page_amount_greater_Tech(client):
    # Set up the session
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = 1
        sess['expense_type'] = 'Tech_assets'
        sess['amount'] = 5001
    response = client.get('/new_request')
    assert response.status_code == 200
    assert b'You cannot claim amount greater than Rs.5000 for Tech Assets' in response.data


def test_admin_dashboard_get(client):
    with client.session_transaction() as sess:
        sess['admin_name'] = 'Admin'
        sess['admin_id'] = 1
    response = client.get('/admin_dashboard')
    assert response.status_code == 200
    assert b'Admin' in response.data


def test_manager_get_page_notloggedin(client):  
    response = client.get('/manager_page')
    assert response.status_code == 400


def test_manager_get_page_loggedin(client):
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = 11
        sess['email_id'] = 'manager@nucleusteq.com'
        sess['password'] = 'manager1'
        sess['user_name'] = 'Manager'
        sess['manager_id'] = 11
    # Perform GET request to the manager_page route
    response = client.get('/manager_page',data={'manager_id':'11'})
    assert response.status_code == 200


def test_manager_review_request_loggedin(client):
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = 11
        sess['email_id'] = 'manager@nucleusteq.com'
        sess['password'] = 'manager1'
        sess['user_name'] = 'Manager'
        sess['manager_id'] = 11   
    response = client.post('/manager_page',data={'manager_id':'11','request_id':'16','status':'Accept','comment':'Approved'})
    assert response.status_code == 200
    


    
def test_admin_dashboard_post(client):
    with client.session_transaction() as sess:
        sess['admin_name'] = 'Admin'
        sess['admin_id'] = 1
    # POST request with valid data
    with client.post('/admin_dashboard', data={'request_id': 1, 'status': 'approved', 'comments': 'Approved'}) as response:
        assert response.status_code == 200

    # Simulate POST request with missing form data
    with client.post('/admin_dashboard', data={}, follow_redirects=True) as response:
        assert response.status_code == 400  


def test_get_admin_assignpage_loggedin(client):
    with client.session_transaction() as sess:
        sess['admin_name'] = 'Admin'
        sess['admin_id'] = 1
    with client.get('/admin_assign') as response:
        assert response.status_code == 200
       

def test_admin_assign_get_managers(client):
    response=client.post('/admin_assign',data={'employee_id':'13','department':'Sales'})
    assert response.status_code==200

def test_admin_assign_managerToemployee(client):
    with client.session_transaction() as sess:
        sess['loggedin']=True
        sess['admin_name'] = 'Admin'
        sess['admin_id'] = 1
        sess['request_id']=13
    response=client.post('/admin_assign_submit',data={'employee_id':'13','manager_id':'11'})
    assert response.status_code==200

def test_admin_dashboard_get_page(client):
    with client.session_transaction() as sess:
        sess['admin_name'] = 'Admin'
        sess['admin_id'] = 1
    with client.get('/admin_dashboard') as response:
        assert response.status_code == 200



def test_admin_deleteDept(client):
 # Simulate POST request to /admin_deleteDept with department_id 1
    response = client.post('/admin_deleteDept', data={'department_id': 1}, follow_redirects=True)
    assert response.status_code == 200
 # Check if department with department_id=1 is deleted
    assert b'department_id: 1' not in response.data

def test_admin_deleteDept_get(client):
    response=client.get('/admin_deleteDept')
    assert response.status_code==200



def test_admin_insertDept_get(client):
    response=client.get('/admin_insertDept')
    assert response.status_code==200



def test_admin_insertDept(client):
    response=client.post('/admin_insertDept',data={'department_name':'Enterprise Information'})
    assert response.status_code==200
    assert b'Department has been successfully inserted' in response.data

def test_admin_deleteEmp_getUsersTable(client):
    response=client.get('/admin_deleteEmp')
    assert response.status_code==200


def test_admin_delete_employeepage_delete_employee(client):
    response=client.post('/admin_deleteEmp',data={'user_id':14})
    assert response.status_code==200
    assert b'user_id: 14' not in response.data

def test_get_admin_audittrail(client):
    response=client.get('admin_audittrail')
    assert response.status_code==200




   



