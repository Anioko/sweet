import importlib

from libs.sweet_apps import get_sweet_apps

sweet_apps = get_sweet_apps()
for sweet_app in sweet_apps:
    # from sweet_app.app_module.models import *
    try:
        mdl = importlib.import_module(f'{sweet_app.app_name}.forms')
        # __import__(f'{sweet_app.app_name}.models', globals=globals())
        if "__all__" in mdl.__dict__:
            names = mdl.__dict__["__all__"]
        else:
            # otherwise we import all names that don't begin with _
            names = [x for x in mdl.__dict__ if not x.startswith("_")]

        # now drag them in
        globals().update({k: getattr(mdl, k) for k in names})
    except:
        pass
