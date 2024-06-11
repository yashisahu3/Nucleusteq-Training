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

def test_get_admin_login_page(client):
    response=client.get('/admin_login')
    assert response.status_code==200
    

def test_admin_login_successful(client):
    response=client.post('/admin_login',data={'email_id':'rajesh.sahu@nucleusteq.com','password':'rajesh123'})
    assert response.status_code==302
    assert '/admin_dashboard' in response.location

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
