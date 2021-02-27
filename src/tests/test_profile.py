import unittest
from main import create_app, db
from helpers import captured_templates
from models.User import Users
from models.Profile import Profile
from models.Locations import Location
from models.ProfileImage import ProfileImage
import forms
import io


class TestProfile(unittest.TestCase):
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

    def login(self, data):
        self.client.post("/web/login", data=data, follow_redirects=True)

    def logout(self):
        self.client.get("/web/logout")

    def test_profile(self):
        data = {
            "username": "tester1",
            "password": "123456"
        }

        self.login(data)
        self.user = Users.query.filter_by(username="tester1").first()
        self.profile = Profile.query.filter_by(user_id=self.user.id).first()
        self.locations = Location.query.filter_by(
            profile_id=self.profile.id).all()
        self.image = ProfileImage.query.filter_by(
            profile_id=self.profile.id).first()
        self.postcodes = []
        for location in self.locations:
            self.postcodes.append(location.postcode)

        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.get("/web/profile/")
                template, context = templates[0]

                self.assertEqual(response.status_code, 200)
                self.assertEqual(template.name, "profile.html")

        response1 = self.client.get("/web/profile/", follow_redirects=True)

        self.assertEqual(response1.status_code, 200)
        self.assertIn((self.profile.name).encode('utf-8'), response1.data)
        self.assertEqual(len(self.locations), 3)
        self.assertIn((self.image.filename).encode("utf-8"), response1.data)

        for location in self.locations:
            self.assertIn(
                str(location.postcode).encode("utf-8"), response1.data)
            self.assertIn((location.suburb).encode("utf-8"), response1.data)

    def test_profile_details(self):
        self.logout()
        data = {
            "username": "tester5",
            "password": "123456"
        }

        self.login(data)
        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.get("/web/profile", follow_redirects=True)
                template, context = templates[0]

                self.assertEqual(response.status_code, 200)
                self.assertEqual(template.name, "profile_name.html")
                self.assertIsInstance(context["form"], forms.ProfileForm)

        response1 = self.client.post("/web/profile/profilename", data={
            "profile_name": "test profile",
        }, follow_redirects=True)

        user = Users.query.filter_by(username="tester5").first()
        profile = Profile.query.filter_by(user_id=user.id).first()

        self.assertTrue(response1.status_code, 200)
        self.assertIn(b"Profile name confirmed!", response1.data)
        self.assertTrue(profile.name, "test profile")
        self.assertTrue(b"default.png", response1.data)

        file_data = {
            "image": (io.BytesIO(b"test"), "test_file.jpg")
        }
        response2 = self.client.post(
            "/web/profile/uploadimage", data=file_data,
            follow_redirects=True, content_type="multipart/form-data")
        image1 = ProfileImage.query.filter_by(profile_id=profile.id).first()

        response3 = self.client.post(
            "/web/profile/deleteimage", follow_redirects=True)
        image2 = ProfileImage.query.filter_by(profile_id=profile.id).first()

        self.assertTrue(response2.status_code, 200)
        self.assertIn((image1.filename).encode("utf-8"), response2.data)
        self.assertIsNone(image2)
        self.assertIn(b"Image removed", response3.data)
        self.assertIn(b"default.png", response1.data)

    def test_profile_locations(self):
        self.logout()
        data = {
            "username": "tester2",
            "password": "123456"
        }
        self.login(data)
        user = Users.query.filter_by(username="tester2").first()
        profile = Profile.query.filter_by(user_id=user.id).first()
        default_locations = Location.query.filter_by(
            profile_id=profile.id).all()
        default_postcodes = [
            location.postcode for location in default_locations]

        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.get(
                    "/web/profile/locationsearch", follow_redirects=True)
                template, context = templates[0]

                self.assertEqual(response.status_code, 200)
                self.assertEqual(template.name, "locations.html")
                self.assertIsInstance(context["form"], forms.SearchLocation)

            with captured_templates(self.app) as templates:
                response = c.post(
                    "/web/profile/locationsearch",
                    data={"postcode": "3000"}, follow_redirects=True)
                template, context = templates[0]

                self.assertIsInstance(context["form2"], forms.AddButton)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"Melbourne", response.data)

        response1 = self.client.post("/web/profile/locationsearch", data={
            "postcode": "100"
        }, follow_redirects=True)
        self.assertIn(
            b"No locations found. Try another postcode", response1.data)

        url = "/web/profile/addlocation?postcode=3000&suburb=Melbourne&state=VIC"   # noqa: E501
        response2 = self.client.post(
            url,
            follow_redirects=True)
        updated_locations = Location.query.filter_by(
            profile_id=profile.id).all()

        if 3000 not in default_postcodes:
            self.assertTrue(len(updated_locations), 4)
            self.assertIn(b"Melbourne", response2.data)
        else:
            self.assertTrue(len(updated_locations), 3)
            self.assertIn(
                b"Suburb already associated with your profile", response2.data)
