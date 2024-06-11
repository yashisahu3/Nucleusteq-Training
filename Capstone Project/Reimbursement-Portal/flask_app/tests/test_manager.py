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

def test_login_successful_manager(client):
    response=client.post('/',data={'email_id':'riya.sharma@nucleusteq.com','password':'riya123'})
    assert response.status_code==200

def test_manager_get_page_notloggedin(client):  
    response = client.get('/manager_page')
    assert response.status_code == 400


def test_submit_request_manager_logged_in(client):
    # Set up the session
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = '11'
    response = client.post('/new_request', data={'user_id':'11','amount': '200','expense_type':'Travelling','date':'2024-05-02','employee_type':'manager',
                                                 'receipt': (BytesIO(b'file content'), 'abc.jpg')})
    assert response.status_code == 200



def test_get_new_request_page(client):
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = 13
    response=client.get('/new_request')
    assert response.status_code==200


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
    