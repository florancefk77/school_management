import pytest
from app import app
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.get_db_connection')
def test_display_teachers(mock_db_conn, client):
    mock_cursor = MagicMock()
    mock_db_conn.return_value.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1, 'first_name': 'Jane', 'last_name': 'Smith'}]

    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 'admin'

    response = client.get('/teachers')
    assert response.status_code == 200
    assert b'Jane Smith' in response.data

@patch('app.get_db_connection')
def test_add_teacher(mock_db_conn, client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 'admin'

    response = client.get('/teachers/add')
    assert response.status_code == 200
    assert b'Add Teacher' in response.data

@patch('app.get_db_connection')
def test_save_teacher(mock_db_conn, client):
    mock_cursor = MagicMock()
    mock_db_conn.return_value.cursor.return_value = mock_cursor

    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 'admin'

    response = client.post('/teachers/save', data={
        'first_name': 'John',
        'last_name': 'Doe',
        'phone': '1234567890',
        'email': 'john@example.com',
        'address': '456 Elm St'
    })
    assert response.status_code == 302  # Redirect after successful addition

@patch('app.get_db_connection')
def test_delete_teacher(mock_db_conn, client):
    mock_cursor = MagicMock()
    mock_db_conn.return_value.cursor.return_value = mock_cursor

    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 'admin'

    response = client.post('/teachers/delete/1')
    assert response.status_code == 302  # Redirect after successful deletion

@patch('app.get_db_connection')
def test_edit_teacher(mock_db_conn, client):
    mock_cursor = MagicMock()
    mock_db_conn.return_value.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {'id': 1, 'first_name': 'Jane', 'last_name': 'Smith'}

    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 'admin'

    response = client.get('/teachers/edit/1')
    assert response.status_code == 200
    assert b'Jane Smith' in response.data
