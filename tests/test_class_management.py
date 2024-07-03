import pytest
from app import app
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.get_db_connection')
def test_display_classes(mock_db_conn, client):
    mock_cursor = MagicMock()
    mock_db_conn.return_value.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'Class A', 'capacity': 30}]

    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 'admin'

    response = client.get('/classes')
    assert response.status_code == 200
    assert b'Class A' in response.data

@patch('app.get_db_connection')
def test_add_class(mock_db_conn, client):
    mock_cursor = MagicMock()
    mock_db_conn.return_value.cursor.return_value = mock_cursor

    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 'admin'

    response = client.post('/classes/add', data={'name': 'New Class', 'capacity': '25'})
    assert response.status_code == 302  # Redirect after successful addition

@patch('app.get_db_connection')
def test_edit_class(mock_db_conn, client):
    mock_cursor = MagicMock()
    mock_db_conn.return_value.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {'id': 1, 'name': 'Class A', 'capacity': 30}

    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 'admin'

    response = client.get('/classes/edit/1')
    assert response.status_code == 200
    assert b'Class A' in response.data

@patch('app.get_db_connection')
def test_delete_class(mock_db_conn, client):
    mock_cursor = MagicMock()
    mock_db_conn.return_value.cursor.return_value = mock_cursor

    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 'admin'

    response = client.post('/classes/delete/1')
    assert response.status_code == 302  # Redirect after successful deletion
