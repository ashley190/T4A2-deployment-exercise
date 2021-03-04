from models.User import Users
from schemas.UserSchema import users_schema
from flask import url_for
from helpers import captured_templates, Helpers
import forms


class TestAuth(Helpers):
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
        endpoint = url_for("auth.register")

        response1 = self.post_request(endpoint, registration_data1)
        response2 = self.post_request(endpoint, registration_data2)
        response3 = self.post_request(endpoint, registration_data3)
        response4 = self.post_request(endpoint, registration_data4)
        self.logout()

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
        response1 = self.login(login_data1)
        self.logout()
        response2 = self.login(login_data2)
        self.logout()
        response3 = self.login(login_data3)
        self.logout()

        self.assertEqual(response1.status_code, 200)
        self.assertIn(b"Profile", response1.data)
        self.assertIn(b"Invalid username and password", response2.data)
        self.assertIn(b"This field is required", response3.data)
