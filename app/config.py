import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///stockflow.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SALES_WINDOW_DAYS = int(os.getenv("SALES_WINDOW_DAYS", "30"))
