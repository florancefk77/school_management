import unittest
from app import app, get_db_connection
from flask import session

class StudentManagementTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor(dictionary=True)
        self.init_db()
        self.populate_db()

    def tearDown(self):
        self.cursor.close()
        self.conn.close()
        self.ctx.pop()

    def login(self, role):
        with self.app.session_transaction() as sess:
            sess['logged_in'] = True
            sess['role'] = role

    def init_db(self):
        self.conn.commit()

    def populate_db(self):
        self.conn.commit()

    def test_display_students(self):
        self.login('Admin')
        response = self.app.get('/students')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Students', response.data)
        self.assertIn(b'John', response.data)
        # self.assertIn(b'Alice', response.data)
        


    def test_add_student_page(self):
        self.login('Admin')
        response = self.app.get('/students/add')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add New Student', response.data)
        
    def test_save_student(self):
        self.login('Admin')
        # # Test adding a new student
        response = self.app.post('/students/save', data=dict(
            first_name='John',
            last_name='Doe',
            phone='1234567890',
            email='john.doe@example.com',
            address='123 Main St',
            class_id='1'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Students', response.data)
        
       
        # Test updating an existing student
        # student_id = student['id']
        response = self.app.post('/students/save', data=dict(
            ID=4,
            first_name='John',
            Last_name='Doe',
            phone='0987654321',
            email='john.doe@example.com',
            address='12345 Main St',
            class_id='1'
        ), follow_redirects=True)
        
    def test_delete_student(self):
        self.login('Admin')
        # response = self.app.post('/students/delete/45', follow_redirects=True)
        # self.assertEqual(response.status_code, 200)
        # self.assertIn(b'Students', response.data)
        


if __name__ == '__main__':
    unittest.main()
