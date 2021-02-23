import os


def get_from_env(var):
    value = os.environ.get(var)

    if not value:
        raise ValueError(f"{var} is not set!")

    return value


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = get_from_env('SECRET_KEY')

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return get_from_env('DB_URI')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:testdb"
    WTF_CSRF_ENABLED = False


environment = os.environ.get("FLASK_ENV")

if environment == "production":
    app_config = ProductionConfig()
elif environment == "testing":
    app_config = TestingConfig()
else:
    app_config = DevelopmentConfig()
