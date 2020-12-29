app_path = '/app'


class SweetApp:
    name = ''
    version = '0.01'
    prefix = '/'
    url_prefix = '/'
    license_key = None
    db_prefix = None
    side_menu = None
    active = True
    app_module = None
    app_path = None

    def __init__(self, app_module, data):
        for key in data.keys():
            self.app_module = app_module
            self.__dict__[key] = data[key]


def get_sweet_apps():
    from sweet_cms import applications
    import pkgutil, importlib, os
    from yaml import load, dump
    try:
        from yaml import CLoader as Loader, CDumper as Dumper
    except ImportError:
        from yaml import Loader, Dumper

    sweet_apps = list(pkgutil.iter_modules(applications.__path__, applications.__name__ + "."))
    sweet_app_instances = []

    for sweet_app in sweet_apps:
        app_name = sweet_app.name
        app_path = os.path.join(sweet_app.module_finder.path, app_name.split('.')[2])
        desc_path = os.path.join(app_path, 'desc.yaml')
        desc = open(desc_path).read()
        data = load(desc, Loader=Loader)
        data['app_name'] = app_name
        data['app_path'] = app_path
        app_module = importlib.import_module(app_name)
        sweet_app_instances.append(SweetApp(app_module, data))
    return sweet_app_instances


def get_sweet_app(search_val, by='name'):
    sweet_apps = get_sweet_apps()
    results = [sweet_app for sweet_app in sweet_apps if sweet_app.__getattribute__(by) == search_val]
    if results:
        return results[0]
    else:
        return None
