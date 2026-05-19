import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://autosolari:autosolari@localhost/autosolari_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
