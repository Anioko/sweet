# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
import importlib
import os

from flask import flash

from libs.sweet_apps import get_sweet_apps


def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text} - {error}", category)


sweet_apps = get_sweet_apps()
for sweet_app in sweet_apps:
    utils_file = os.path.join(sweet_app.app_path, 'utils.py')
    if os.path.exists(utils_file):
            mdl = importlib.import_module(f'{sweet_app.app_name}.utils')
            if "__all__" in mdl.__dict__:
                names = mdl.__dict__["__all__"]
            else:
                names = [x for x in mdl.__dict__ if not x.startswith("_")]
            globals().update({k: getattr(mdl, k) for k in names})
