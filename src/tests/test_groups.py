from helpers import captured_templates, Helpers
from flask import url_for
from models.Profile import Profile
from models.User import Users
from models.Groups import Groups
from models.Group_members import GroupMembers
from models.Locations import Location
import forms


class TestGroups(Helpers):
    """TestGroups testcase inheriting from the Helpers testcase class.
    SetUp, TearDown and common class methods inherited from Helpers class."""
    def test_group(self):
        """Tests rendering of groups page and compare rendering data
        with data retrieved from test database."""

        # login as "tester2"
        data = {
            "username": "tester2",
            "password": "123456"
        }
        self.login(data)

        # test captured template and forms for groups_page
        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.get(url_for("groups.groups_page"))
                template, context = templates[0]

                self.assertEqual(response.status_code, 200)
                self.assertEqual(template.name, "groups.html")
                self.assertIsInstance(context["form"], forms.JoinButton)
                self.assertIsInstance(context["form2"], forms.UnjoinButton)
                self.assertIsInstance(context["form3"], forms.DeleteButton)

        # retrieve related data from test database
        self.profile = Profile.query.join(
            Users).filter(Users.username == "tester2").first()
        self.profile_locations = Location.query.join(
            Profile).filter(Profile.id == self.profile.id).all()
        self.groups = Groups.query.with_entities(
            Groups.name, Location.postcode, Location.suburb,
            Location.state).join(GroupMembers).filter_by(
                profile_id=self.profile.id).join(Location).all()
        self.non_groups = Groups.query.with_entities(
            Groups.name, Location.postcode, Location.suburb,
            Location.state).join(GroupMembers).filter(
                GroupMembers.profile_id != self.profile.id).join(
                    Location).all()

        # test expected response from get request go groups_page endpoint
        response1 = self.get_request(url_for("groups.groups_page"))

        self.assertEqual(response1.status_code, 200)
        for group in self.groups:
            self.assertIn(self.encode(group.name), response1.data)
            self.assertIn(self.encode(f"{group.postcode}"), response1.data)
        for location in self.profile_locations[-2:]:
            self.assertIn(self.encode(f"{location.postcode}"), response1.data)
            self.assertIn(self.encode(location.suburb), response1.data)
            self.assertIn(self.encode(location.state), response1.data)
