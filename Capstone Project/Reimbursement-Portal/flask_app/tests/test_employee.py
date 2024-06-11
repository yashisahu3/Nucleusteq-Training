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
    

def test_register_invalid_email_address(client):
    response=client.post('/register',data={'email_id':'yashisahu30@gmail.com','password':'abc',
                                           'username':'Yashi','department':'Marketing','employee_type':'manager'})
    assert response.status_code==200
    assert b'Please enter a valid company email address only' in response.data

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
