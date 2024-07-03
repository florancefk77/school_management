import pytest
from app import app
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.get_db_connection')
def test_display_students(mock_db_conn, client):
    mock_cursor = MagicMock()
    mock_db_conn.return_value.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1, 'first_name': 'John', 'last_name': 'Doe'}]

    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 'admin'

    response = client.get('/students')
    assert response.status_code == 200
    assert b'John Doe' in response.data

@patch('app.get_db_connection')
def test_add_student(mock_db_conn, client):
    mock_cursor = MagicMock()
    mock_db_conn.return_value.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'Class A'}]

    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 'admin'

    response = client.get('/students/add')
    assert response.status_code == 200
    assert b'Add Student' in response.data

@patch('app.get_db_connection')
def test_save_student(mock_db_conn, client):
    mock_cursor = MagicMock()
    mock_db_conn.return_value.cursor.return_value = mock_cursor

    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 'admin'

    response = client.post('/students/save', data={
        'first_name': 'Jane',
        'last_name': 'Doe',
        'phone': '1234567890',
        'email': 'jane@example.com',
        'address': '123 Main St',
        'class_id': '1'
    })
    assert response.status_code == 302  # Redirect after successful addition

@patch('app.get_db_connection')
def test_delete_student(mock_db_conn, client):
    mock_cursor = MagicMock()
    mock_db_conn.return_value.cursor.return_value = mock_cursor

    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 'admin'

    response = client.post('/students/delete/1')
    assert response.status_code == 302  # Redirect after successful deletion
