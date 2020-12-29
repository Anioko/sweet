import os
from pathlib import Path

from environs import Env

custom_app_env = Env()
custom_app_env.read_env(recurse=False)
EVENTY_UPLOADS_DIR = custom_app_env.str("EVENTY_UPLOADS_DIR", default="uploads/")
