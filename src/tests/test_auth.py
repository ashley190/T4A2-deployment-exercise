import unittest
from main import create_app, db
from flask import template_rendered
from contextlib import contextmanager
import forms


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


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
                response = c.get('/registration')
                template, context = templates[0]

                self.assertEqual(response.status_code, 200)
                self.assertEqual(template.name, 'register.html')
                self.assertIsInstance(context["form"], forms.RegistrationForm)
