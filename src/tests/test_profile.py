from helpers import captured_templates, Helpers
from flask import url_for
from models.User import Users
from models.Profile import Profile
from models.Locations import Location
from models.ProfileImage import ProfileImage
import forms
import io


class TestProfile(Helpers):
    """TestProfile testcase inheriting from the Helpers testcase class.
    SetUp, TearDown and common class methods inherited from Helpers class."""
    def test_profile(self):
        """Tests rendering of profile page and compare rendered data
        with data retrieved from test database"""

        # login as "tester1"
        data = {
            "username": "tester1",
            "password": "123456"
        }
        self.login(data)

        # retrieve data from database related to username=tester1
        self.user = Users.query.filter_by(username="tester1").first()
        self.profile = Profile.query.filter_by(user_id=self.user.id).first()
        self.locations = Location.query.filter_by(
            profile_id=self.profile.id).all()
        self.image = ProfileImage.query.filter_by(
            profile_id=self.profile.id).first()
        self.postcodes = []
        for location in self.locations:
            self.postcodes.append(location.postcode)

        # test captured template for profile_page
        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.get("/web/profile/")
                template, context = templates[0]

                self.assertEqual(response.status_code, 200)
                self.assertEqual(template.name, "profile.html")

        # retrieve profile page for logged in user (tester1) and test against
        # database data for user(tester1). Logout user once completed
        response1 = self.get_request(url_for("profile.profile_page"))

        self.assertEqual(response1.status_code, 200)
        self.assertIn((self.profile.name).encode('utf-8'), response1.data)
        self.assertEqual(len(self.locations), 7)
        self.assertIn((self.image.filename).encode("utf-8"), response1.data)
        for location in self.locations:
            self.assertIn(
                str(location.postcode).encode("utf-8"), response1.data)
            self.assertIn((location.suburb).encode("utf-8"), response1.data)

        self.logout()

    def test_profile_details(self):
        """Tests logic flow for users without a profile name
        i.e. add profile name, add and remove profile image"""

        # login as tester5(does not have profile name)
        data = {
            "username": "tester5",
            "password": "123456"
        }
        self.login(data)

        # test captured template for new users without a profile name
        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.get("/web/profile", follow_redirects=True)
                template, context = templates[0]

                self.assertEqual(response.status_code, 200)
                self.assertEqual(template.name, "profile_name.html")
                self.assertIsInstance(context["form"], forms.ProfileForm)

        # test addition of profile name for new user against database
        data = {
            "profile_name": "test profile"
        }
        endpoint = url_for("profile.profile_name")
        response1 = self.post_request(endpoint, data)

        user = Users.query.filter_by(username="tester5").first()
        profile = Profile.query.filter_by(user_id=user.id).first()

        self.assertTrue(response1.status_code, 200)
        self.assertIn(b"Profile name confirmed!", response1.data)
        self.assertTrue(profile.name, "test profile")
        self.assertTrue(b"default.png", response1.data)

        # test profile image upload and removal for new user.
        # Logout user once completed
        file_data = {
            "image": (io.BytesIO(b"test"), "test_file.jpg")
        }
        endpoint2 = url_for("profile.profile_image")
        response2 = self.post_request(
            endpoint2, file_data, content_type="multipart/form-data")
        image1 = ProfileImage.query.filter_by(profile_id=profile.id).first()

        endpoint3 = url_for("profile.remove_image")
        response3 = self.post_request(endpoint3)
        image2 = ProfileImage.query.filter_by(profile_id=profile.id).first()

        self.assertTrue(response2.status_code, 200)
        self.assertIn((image1.filename).encode("utf-8"), response2.data)
        self.assertIsNone(image2)
        self.assertIn(b"Image removed", response3.data)
        self.assertIn(b"default.png", response1.data)

        self.logout()

    def test_profile_locations(self):
        """Tests logic flow and external API query for retrieving
        and associating locations based on postcodes
        to a user profile."""

        # Login as a separate user (tester2) and retrieve user-related
        # data from seeded database.
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

        # testing rendering of the correct template and context for the
        # location search endpoint
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

        # Testing location search for an invalid postcode (response1)
        # and valid postcode (response2)
        endpoint = url_for("profile.profile_locations")
        data = {"postcode": "1000"}
        response1 = self.post_request(endpoint, data)
        self.assertIn(
            b"No locations found. Try another postcode", response1.data)

        endpoint2 = "/web/profile/addlocation?postcode=3000&suburb=Melbourne&state=VIC"   # noqa: E501
        response2 = self.post_request(endpoint2)
        updated_locations = Location.query.filter_by(
            profile_id=profile.id).all()

        if 3000 not in default_postcodes:
            self.assertTrue(len(updated_locations), 4)
            self.assertIn(b"Melbourne", response2.data)
        else:
            self.assertTrue(len(updated_locations), 3)
            self.assertIn(
                b"Suburb already associated with your profile", response2.data)
