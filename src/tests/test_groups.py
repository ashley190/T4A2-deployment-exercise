from controllers.controller_helpers import Helpers as cont_helpers
from flask import url_for
from models.Profile import Profile
from models.User import Users
from models.Groups import Groups
from models.Group_members import GroupMembers
from models.Locations import Location
from helpers import captured_templates, Helpers
import forms
import random


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

        self.logout()

    def test_create_group(self):
        data = {
            "username": "tester3",
            "password": "123456"
        }
        self.login(data)

        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.get(url_for("groups.create_group"))
                template, context = templates[0]

                self.assertEqual(template.name, "create_group.html")
                self.assertIsInstance(context["form"], forms.SearchLocation)
                self.assertIsInstance(context["form2"], forms.CreateGroup)

        # test postcode search logic(invalid postcode)
        data1 = {
            "postcode": "1000"
        }

        # test postcode search logic(valid postcode)
        data2 = {
            "postcode": "2000"
        }

        # external api search results for comparison
        api_search = cont_helpers.location_search(2000)
        api_results = [result["name"]for result in api_search]
        location_options = [(index, (location["name"], location[
            "state"]["abbreviation"])) for index, location in enumerate(
                api_search)]

        # test postcode search function on create group page
        endpoint1 = url_for("groups.create_group")

        response1 = self.post_request(endpoint1, data1)
        response2 = self.post_request(endpoint1, data2)

        self.assertEqual(response1.status_code, 200)
        self.assertIn(b"Not a valid postcode", response1.data)
        self.assertEqual(response2.status_code, 200)
        for location in api_results:
            self.assertIn(self.encode(location), response2.data)

        # test group creation logic
        form = forms.CreateGroup()
        form.group_location.choices = location_options
        endpoint2 = url_for(
            "groups.create_group", locations=form.group_location,
            data=api_search)

        create_data1 = {
            "group_name": "new group",
            "group_description": "new group description",
            "group_location": 2
        }

        # test create group logic against database data as well as redirect
        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.post(
                    endpoint2, data=create_data1, follow_redirects=True)
                template, context = templates[0]

                new_group = Groups.query.with_entities(
                    Groups.name, Location.postcode, Location.suburb,
                    Location.state, GroupMembers.admin).filter_by(
                        name=create_data1["group_name"]).join(
                            GroupMembers).join(Location).first()

                self.assertEqual(template.name, "groups.html")
                self.assertEqual(response.status_code, 200)
                self.assertIn(self.encode(new_group.name), response.data)
                self.assertIn(
                    self.encode(f"{new_group.postcode}"), response.data)
                self.assertIn(self.encode(
                    f"{new_group.suburb}, {new_group.state}"), response.data)
                self.assertEqual(new_group.suburb, "Millers Point")
                self.assertEqual(new_group.state, "NSW")
                self.assertTrue(new_group.admin)

        self.logout()

    def test_group_details(self):
        """Tests rendering of group details page"""
        data = {
            "username": "tester4",
            "password": "123456"
        }

        self.login(data)

        # retrieve all groups
        all_groups = Groups.query.with_entities(
            Groups.id, Groups.name, Groups.description, Location.postcode,
            Location.suburb, Location.state).join(Location).all()

        # test captured template and context group_detail page for all groups
        for group in all_groups:
            with self.client as c:
                with captured_templates(self.app) as templates:
                    c.get(url_for("groups.group_details", id=group.id))
                    template, context = templates[0]

                    self.assertEqual(template.name, "group_detail.html")
                    self.assertEqual(group.name, context["group_name"])
                    self.assertEqual(
                        group.description, context["group_description"])
                    self.assertEqual(
                        f"{group.suburb}, {group.state}", context[
                            "group_location"])

        self.logout()

    def test_update_group(self):
        """Test rendering and logic of update group page"""

        # login as valid user
        data = {
            "username": "tester1",
            "password": "123456"
        }
        self.login(data)

        # set up variables for endpoint testing with:-
        # 1 group id where user is admin
        # 1 group id where user is member but not admin
        # 1 group id where user is not a member
        # data to be used for post request to update group details
        member_groups = GroupMembers.query.filter_by(profile_id=1).all()
        member_groupids = [group.group_id for group in member_groups]
        non_member_groups = GroupMembers.query.filter(
            GroupMembers.group_id.notin_(member_groupids)).all()

        self.post_request(url_for(
            "groups.join_group", id=non_member_groups[0].group_id))
        member_groups = GroupMembers.query.filter_by(profile_id=1).all()
        member_groupids = [group.group_id for group in member_groups]
        non_member_groups = GroupMembers.query.filter(
            GroupMembers.group_id.notin_(member_groupids)).all()

        selected_admin_id = member_groupids[0]
        selected_non_admin_id = member_groupids[-1]
        selected_non_member_id = random.choice(non_member_groups)

        data = {
            "group_name": "Updated group name",
            "description": ""
        }

        # test captured templates and logic on successful get and
        # post requests (valid group admin)
        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.get(
                    url_for("groups.update_group", id=selected_admin_id),
                    follow_redirects=True)
                template, context = templates[0]

                location = Location.query.filter_by(
                    group_id=selected_admin_id).first()

                self.assertEqual(template.name, "update_group.html")
                self.assertIsInstance(context["form"], forms.UpdateGroup)
                self.assertEqual(context["location"], location)

            with captured_templates(self.app) as templates:
                response = c.post(
                    url_for("groups.update_group", id=selected_admin_id),
                    data=data, follow_redirects=True)
                template, context = templates[0]

                location = Location.query.filter_by(
                    group_id=selected_admin_id).first()

                self.assertEqual(template.name, "groups.html")
                self.assertEqual(response.status_code, 200)
                self.assertIn(self.encode(
                    f"{data['group_name']}"), response.data)
                self.assertIn(self.encode("Group updated"), response.data)
                self.assertIn(self.encode(
                    f"{location.suburb}, {location.state}"), response.data)

        # test get and post requests for non-group admins and non-members
        response_1 = self.get_request(url_for(
            "groups.update_group", id=selected_non_admin_id))
        response_2 = self.get_request(url_for(
            "groups.update_group", id=selected_non_member_id.group_id))
        response_3 = self.post_request(url_for(
            "groups.update_group", id=selected_non_admin_id), data=data)
        response_4 = self.post_request(
            url_for("groups.update_group", id=selected_non_member_id.group_id),
            data=data)

        self.assertEqual(response_1.status_code, 401)
        self.assertEqual(response_2.status_code, 401)
        self.assertEqual(response_3.status_code, 401)
        self.assertEqual(response_4.status_code, 401)

        self.logout()

    def test_update_group_location(self):
        """Test rendering and logic for update group location page"""

        # login as valid user
        data = {
            "username": "tester2",
            "password": "123456"
        }
        self.login(data)

        # set up variables for endpoint testing with:-
        # 1 group id where user is admin
        # 1 group id where user is member but not admin
        # 1 group id where user is not a member
        # data to be used for post request to update group location
        member_groups = GroupMembers.query.filter_by(profile_id=2).all()
        member_groupids = [group.group_id for group in member_groups]
        non_member_groups = GroupMembers.query.filter(
            GroupMembers.group_id.notin_(member_groupids)).all()

        self.post_request(url_for(
            "groups.join_group", id=non_member_groups[0].group_id))
        member_groups = GroupMembers.query.filter_by(profile_id=2).all()
        member_groupids = [group.group_id for group in member_groups]
        non_member_groups = GroupMembers.query.filter(
            GroupMembers.group_id.notin_(member_groupids)).all()

        selected_admin_id = member_groupids[0]
        selected_non_admin_id = member_groupids[-1]
        selected_non_member_id = random.choice(non_member_groups)

        data = {
            "postcode": "3040"
        }

        # test captured templates and logic on successful get and
        # post requests (valid group admin)
        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.get(url_for(
                    "groups.update_group_location",
                    id=selected_admin_id), follow_redirects=True)
                template, context = templates[0]

                self.assertEqual(template.name, "group_location.html")
                self.assertIsInstance(context["form"], forms.SearchLocation)

            with captured_templates(self.app) as templates:
                response = c.post(url_for(
                    "groups.update_group_location",
                    id=selected_admin_id), data=data, follow_redirects=True)
                template, context = templates[0]

                locations = cont_helpers.location_search(data["postcode"])

                self.assertEqual(template.name, "group_location.html")
                self.assertIsInstance(context["form"], forms.SearchLocation)
                self.assertIsInstance(context["form2"], forms.UpdateButton)
                self.assertEqual(response.status_code, 200)
                for location in locations:
                    self.assertIn(self.encode(
                        f"{location['postcode']}"), response.data)
                    self.assertIn(self.encode(
                        location["name"]), response.data)
                    self.assertIn(self.encode(
                        location["state"]["abbreviation"]), response.data)

        # test get and post requests for non-group admins and non-members
        response_1 = self.get_request(url_for(
            "groups.update_group_location", id=selected_non_admin_id))
        response_2 = self.get_request(url_for(
            "groups.update_group_location",
            id=selected_non_member_id.group_id))
        response_3 = self.post_request(url_for(
            "groups.update_group_location",
            id=selected_non_admin_id), data=data)
        response_4 = self.post_request(url_for(
            "groups.update_group_location",
            id=selected_non_member_id.group_id), data=data)

        self.assertEqual(response_1.status_code, 401)
        self.assertEqual(response_2.status_code, 401)
        self.assertEqual(response_3.status_code, 401)
        self.assertEqual(response_4.status_code, 401)

        self.logout()
