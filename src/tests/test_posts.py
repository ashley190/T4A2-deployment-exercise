import unittest
from models.Group_members import GroupMembers
from models.Posts import Posts
from models.Comments import Comments
from helpers import captured_templates, Helpers
from flask import url_for
import forms


class TestPosts(Helpers):
    """TestPosts testcase inheriting from the Helpers testcase class.
    SetUp, TearDown and common class methods inherited from Helpers class."""
    def test_create_group_posts(self):
        """Tests rendering of create posts page and test post creation logic
        with rendred template and against database"""

        # login as a valid user
        data = {
            "username": "tester2",
            "password": "123456"
        }
        self.login(data)

        # prepare required variable for post creation testing
        admin_groups = GroupMembers.query.filter_by(profile_id=2, admin=True).all()
        admin_groupids = [x.group_id for x in admin_groups]
        non_admin_groups = GroupMembers.query.filter_by(profile_id=2, admin=False).all()
        non_admin_groupids = [x.group_id for x in non_admin_groups]
        non_member_groupids = [num for num in range(1, 9)if num not in (admin_groupids + non_admin_groupids)]

        # test captured template when get request is made to the create post endpoint
        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.get(url_for("posts.create_group_posts", id=non_admin_groupids[0]))
                template, context = templates[0]

                self.assertEqual(template.name, "new_post.html")
                self.assertIsInstance(context["form"], forms.CreatePost)
        
        # post request testing with 3 endpoints
        # endpoints 1 and 2 are valid posters (admin and group member)
        # endpoint 3 is an invalid poster (non-group member)
        endpoint1 = url_for("posts.create_group_posts", id=admin_groupids[0])
        endpoint2 = url_for("posts.create_group_posts", id=non_admin_groupids[0])
        endpoint3 = url_for("posts.create_group_posts", id=non_member_groupids[0])

        data = {
            "post": "A new post."
        }

        # test post requests to endpoint 1
        db_before = Posts.query.filter_by(group_id=admin_groupids[0], profile_id=2).first()
        response1 = self.post_request(endpoint1, data=data)
        db_after = Posts.query.filter_by(group_id=admin_groupids[0], profile_id=2).first()

        self.assertEqual(response1.status_code, 200)
        self.assertIn(self.encode(data["post"]), response1.data)
        self.assertIsNone(db_before)
        self.assertIsNotNone(db_after)
        self.assertEqual(db_after.post, data["post"])

        # test post requests to endpoint 2
        db_before = Posts.query.filter_by(group_id=non_admin_groupids[0], profile_id=2).first()
        response2 = self.post_request(endpoint2, data=data)
        db_after = Posts.query.filter_by(group_id=non_admin_groupids[0], profile_id=2).first()

        self.assertEqual(response2.status_code, 200)
        self.assertIn(self.encode(data["post"]), response2.data)
        self.assertIsNone(db_before)
        self.assertIsNotNone(db_after)
        self.assertEqual(db_after.post, data["post"])

        # test post requests to endpoint 3
        response3 = self.post_request(endpoint3, data=data)

        self.assertEqual(response3.status_code, 401)
        self.assertIn(b"Unauthorised to create post", response3.data)

        self.logout()

    def test_post_comment(self):
        # login as a valid user
        data = {
            "username": "tester1",
            "password": "123456"
        }
        self.login(data)

        # join group with existing post (Group3)
        # retrieve post in Group 3 
        self.post_request(url_for("groups.join_group", id=3))
        gp_post = Posts.query.filter_by(group_id=3).first()

        # test captured template when get request is made to the add comment endpoint
        with self.client as c:
            with captured_templates(self.app) as templates:
                response = c.get(url_for("posts.post_comment", id=gp_post.id))
                template, context = templates[0]

                self.assertEqual(template.name, "comment.html")
                self.assertIsInstance(context["form"], forms.Comment)
        
        # test valid post request to add comment to a post
        endpoint = url_for("posts.post_comment", id=gp_post.id)
        data = {
            "comment": "A new comment"
        }

        db_before = Comments.query.filter_by(post_id=gp_post.id).first()
        response1 = self.post_request(endpoint, data)
        db_after = Comments.query.filter_by(post_id=gp_post.id).first()

        self.assertEqual(response1.status_code, 200)
        self.assertIn(self.encode(data["comment"]), response1.data)
        self.assertIsNone(db_before)
        self.assertIsNotNone(db_after)
        self.assertEqual(data["comment"], db_after.comment)

        self.logout()

        # testing for invalid add comment operation(by a non-member)
        # log in as non-member of group 1 
        data = {
            "username": "tester2",
            "password": "123456"
        }
        self.login(data)

        # retrieve post from group 1 and create endpoint
        gp1_post = Posts.query.filter_by(group_id=1).first()
        endpoint2 = url_for("posts.post_comment", id=gp1_post.id)
        data = {
            "comment": "A new comment"
        }

        # test invalid post request to create a comment (by a non-member)
        response2 = self.post_request(endpoint2, data=data)

        self.assertEqual(response2.status_code, 401)
        self.assertIn(self.encode("Unauthorised to comment."), response2.data)

        self.logout()
