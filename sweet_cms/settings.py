# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""
import importlib
import os
from pathlib import Path

from environs import Env

from libs.sweet_apps import get_sweet_apps

env = Env()
env.read_env()

ENV = env.str("FLASK_ENV", default="production")
UPLOAD_DIR = env.str("UPLOAD_DIR", default="uploads")
DEBUG = ENV == "development"
SQLALCHEMY_DATABASE_URI = env.str("DATABASE_URL")
SECRET_KEY = env.str("SECRET_KEY")
SEND_FILE_MAX_AGE_DEFAULT = env.int("SEND_FILE_MAX_AGE_DEFAULT")
BCRYPT_LOG_ROUNDS = env.int("BCRYPT_LOG_ROUNDS", default=13)
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False
CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False
REVERSE_PROXY = env.int("REVERSE_PROXY") if "REVERSE_PROXY" in os.environ else 0
REVERSE_PROXY_PATH = env.str("REVERSE_PROXY_PATH") if "REVERSE_PROXY_PATH" in os.environ else '/'
BASE_DIR = Path(__file__).resolve()
UPLOADED_IMAGES_DEST = os.path.join(os.path.dirname(os.path.realpath(__file__)), UPLOAD_DIR, 'images')
UPLOADED_VIDEOS_DEST = os.path.join(os.path.dirname(os.path.realpath(__file__)), UPLOAD_DIR, 'videos')
UPLOADED_IMAGESVIDEOS_DEST = os.path.join(os.path.dirname(os.path.realpath(__file__)), UPLOAD_DIR)
RQ_REDIS_URL = 'redis://localhost:6379'
PAGINATE_PAGE_SIZE=20
sweet_apps = get_sweet_apps()
for sweet_app in sweet_apps:
    settings_file = os.path.join(sweet_app.app_path, 'settings.py')
    if os.path.exists(settings_file):
        mdl = importlib.import_module(f'{sweet_app.app_name}.settings')
        if "__all__" in mdl.__dict__:
            names = mdl.__dict__["__all__"]
        else:
            names = [x for x in mdl.__dict__ if not x.startswith("_")]
        globals().update({k: getattr(mdl, k) for k in names})
