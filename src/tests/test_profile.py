# import unittest
# from main import create_app, db


# class TestProfile(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.app = create_app()
#         cls.app_context = cls.app.app_context()
#         cls.app_context.push()
#         cls.client = cls.app.test_client()
#         db.create_all()

#         runner = cls.app.test_cli_runner()
#         result = runner.invoke(args=["db-custom", "seed"])
#         if result.exit_code != 0:
#             raise ValueError(result.stdout)

#     @classmethod
#     def tearDownClass(cls):
#         db.session.remove()
#         db.drop_all()
#         cls.app_context.pop()

#     def test_profile_page(self):
#         response = self.client.get("/profile/")

#         self.assertEqual(response.status_code, 302)
