import unittest
from main import create_app, db
from flask import template_rendered
from contextlib import contextmanager


@contextmanager
def captured_templates(app):
    """Helper context manager that captures template rendered
    and variables passed to template.
    Used in conjunction with testing client."""
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class Helpers(unittest.TestCase):
    """Helper class that sets up and tears down test case at a class level.
    Also contains frequently used methods as class methods such as
    login, logout, post and get requests."""
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app_context = cls.app.app_context()
        cls.context = cls.app.test_request_context()
        cls.app_context.push()
        cls.context.push()
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
        cls.context.pop()

    @classmethod
    def login(cls, data):
        return cls.client.post("/web/login", data=data, follow_redirects=True)

    @classmethod
    def logout(cls):
        cls.client.get("/web/logout")

    @classmethod
    def post_request(cls, endpoint, data=None, content_type=None):
        return cls.client.post(
            endpoint, data=data, content_type=content_type,
            follow_redirects=True)

    @classmethod
    def get_request(cls, endpoint):
        return cls.client.get(endpoint, follow_redirects=True)
