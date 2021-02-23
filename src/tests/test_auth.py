import unittest
from models.User import Users
from schemas.UserSchema import users_schema
from main import create_app, db
from helpers import captured_templates
import forms


class TestAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.client = cls.app.test_client()
        db.create_all()

        runner = cls.app.test_cli_runner()
        result = runner.invoke(args=["db-custom", "seed"])
        if result.exit_code != 0:
            raise ValueError(result.stdout)

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def test_register(self):
        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.get("/web/registration")
                template, context = templates[0]

                self.assertEqual(response.status_code, 200)
                self.assertEqual(template.name, 'register.html')
                self.assertIsInstance(context["form"], forms.RegistrationForm)

        registration_data1 = {
            "username": "testera",
            "password": "password1.",
            "confirm": "password1."
            }

        registration_data2 = {
            "username": "test1",
            "password": "password1.",
            "confirm": "password1."
        }

        registration_data3 = {
            "username": "testerb",
            "password": "pw.",
            "confirm": "pw."
        }

        registration_data4 = {
            "username": "testerb",
            "password": "password1.",
            "confirm": "password2."
        }

        response1 = self.client.post(
            "/web/registration",
            data=registration_data1,
            follow_redirects=True)
        self.client.get("/web/logout")
        response2 = self.client.post(
            "/web/registration", data=registration_data2)
        response3 = self.client.post(
            "/web/registration", data=registration_data3)
        response4 = self.client.post(
            "/web/registration", data=registration_data4)

        users = Users.query.all()
        data = users_schema.dump(users)

        self.assertEqual(response1.status_code, 200)
        self.assertIn(b"Profile", response1.data)
        self.assertEqual(data[5]["username"], "testera")
        self.assertIn(
            b"Field must be at least 6 characters long.", response2.data)
        self.assertIn(
            b"Password must be at least 8 characters", response3.data)
        self.assertIn(b"Password must match.", response4.data)

    def test_login(self):
        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.get('/web/login')
                template, context = templates[0]

                self.assertEqual(response.status_code, 200)
                self.assertEqual(template.name, 'login.html')
                self.assertIsInstance(context["form"], forms.LoginForm)

        login_data1 = {
            "username": "tester1",
            "password": "123456"
        }

        login_data2 = {
            "username": "tester11",
            "password": "123456"
        }

        login_data3 = {
            "username": "",
            "password": ""
        }
        response1 = self.client.post(
            "/web/login", data=login_data1, follow_redirects=True)
        self.client.get("/web/logout")
        response2 = self.client.post(
            "/web/login", data=login_data2, follow_redirects=True)
        self.client.get("/web/logout")
        response3 = self.client.post(
            "/web/login", data=login_data3, follow_redirects=True)

        self.assertEqual(response1.status_code, 200)
        self.assertIn(b"Profile", response1.data)
        self.assertIn(b"Invalid username and password", response2.data)
        self.assertIn(b"This field is required", response3.data)
