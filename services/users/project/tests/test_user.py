import json
import unittest
from project import db
from project.api.models import User

from project.tests.base import BaseTestCase


def add_user(username, email):
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return user


class TestUserService(BaseTestCase):

    def test_users(self):
        response = self.client.get('/users/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'potato',
                    'email': 'potato@example.com'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('potato@example.com was added!', data['message'])
            self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({'email': 'potato@example.com'}),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_email(self):
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'potato',
                    'email': 'potato@example.com'
                }),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': "potato",
                    'email': 'potato@example.com'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That email already exists.', data['message']
            )
            self.assertIn('fail', data['status'])

    def test_single_user(self):
        user = add_user('Potato', 'potato@example.com')
        with self.client:
            response = self.client.get(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('Potato', data['data']['username'])
            self.assertIn('potato@example.com', data['data']['email'])
            self.assertIn('success', data['status'])

    def test_single_user_no_id(self):
        with self.client:
            response = self.client.get('/users/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        with self.client:
            response = self.client.get('/users/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_users(self):
        add_user('potato', 'potato@example.com')
        add_user('potatochip', 'chip@example.com')
        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['users']), 2)
            self.assertIn('potato', data['data']['users'][0]['username'])
            self.assertIn(
                'potato@example.com',
                data['data']['users'][0]['email']
            )
            self.assertIn('potatochip', data['data']['users'][1]['username'])
            self.assertIn(
                'chip@example.com',
                data['data']['users'][1]['email']
            )
            self.assertIn('success', data['status'])

    def test_main_no_users(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All users', response.data)
        self.assertIn(b'<p>No users found</p>', response.data)

    def test_main_with_users(self):
        add_user('potato', 'chip@example.com')
        add_user('poos', 'poos@example.com')
        with self.client.get('/'):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All users', response.data)
            self.assertNotIn(b'<p>No users found</p>', response.data)
            self.assertIn(b'potato', response.data)
            self.assertIn(b'poos', response.data)

    def test_main_add_user(self):
        with self.client:
            response = self.client.post(
                '/',
                data=dict(username='potato', email='potato@example.com'),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All users', response.data)
            self.assertNotIn(b'<p>No users found</p>', response.data)
            self.assertIn(b'potato', response.data)


if __name__ == '__main__':
    unittest.main()
