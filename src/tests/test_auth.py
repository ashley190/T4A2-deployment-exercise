from models.User import Users
from schemas.UserSchema import users_schema
from flask import url_for
from helpers import captured_templates, Helpers
import forms


class TestAuth(Helpers):
    """TestAuth testcase inheriting from Helpers testcase class.
    SetUp, TearDown and common class methods inherited from Helpers class.
    """
    def test_register(self):
        """Tests rendering of registration page and registration logic"""

        # test captured template and form for registration page
        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.get(url_for("auth.register"))
                template, context = templates[0]

                self.assertEqual(response.status_code, 200)
                self.assertEqual(template.name, 'register.html')
                self.assertIsInstance(context["form"], forms.RegistrationForm)

        # test registration data
        registration_data1 = {
            "username": "testera",
            "password": "password1.",
            "confirm": "password1."
            }

        # registration data (username too short)
        registration_data2 = {
            "username": "test1",
            "password": "password1.",
            "confirm": "password1."
        }

        # registration data(password too short)
        registration_data3 = {
            "username": "testerb",
            "password": "pw.",
            "confirm": "pw."
        }
        
        #registration data (password mismatch)
        registration_data4 = {
            "username": "testerb",
            "password": "password1.",
            "confirm": "password2."
        }
        endpoint = url_for("auth.register")

        # test registration attempts for each registration data above.
        # Test for expected response data as well as compare successful
        # registration with data in test db.
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
        """Test  rendering of login page as well as login logic"""

        #test captured template and form for login page
        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.get(url_for("auth.login"))
                template, context = templates[0]

                self.assertEqual(response.status_code, 200)
                self.assertEqual(template.name, 'login.html')
                self.assertIsInstance(context["form"], forms.LoginForm)

        # test login data(correct credentials)
        login_data1 = {
            "username": "tester1",
            "password": "123456"
        }

        # test login data(incorrect username)
        login_data2 = {
            "username": "tester11",
            "password": "123456"
        }

        # test login data(blank fields)
        login_data3 = {
            "username": "",
            "password": ""
        }

        # test response acquired from login request
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
