import os


def get_from_env(var):
    value = os.environ.get(var)

    if not value:
        raise ValueError(f"{var} is not set!")

    return value


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024

    @property
    def SECRET_KEY(self):
        return get_from_env('SECRET_KEY')

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return get_from_env('DB_URI')

    @property
    def AWS_ACCESS_KEY_ID(self):
        return get_from_env("AWS_ACCESS_KEY_ID")

    @property
    def AWS_SECRET_ACCESS_KEY(self):
        return get_from_env("AWS_SECRET_ACCESS_KEY")

    @property
    def AWS_S3_BUCKET(self):
        return get_from_env("AWS_S3_BUCKET")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return get_from_env('TESTING_DB_URI')
    TESTING = True
    WTF_CSRF_ENABLED = False
    # SECRET_KEY = "testing"
    # AWS_ACCESS_KEY_ID = 1
    # AWS_SECRET_ACCESS_KEY = 1
    # AWS_S3_BUCKET = 1


environment = os.environ.get("FLASK_ENV")

if environment == "production":
    app_config = ProductionConfig()
elif environment == "testing":
    app_config = TestingConfig()
else:
    app_config = DevelopmentConfig()
