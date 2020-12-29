# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import logging
import sys

from flask import Flask, render_template
from flask_uploads import configure_uploads

from libs.sweet_apps import get_sweet_apps
from libs.sweet_theming import themed_template
from sweet_cms import commands
from sweet_cms.extensions import (
    bcrypt,
    cache,
    csrf_protect,
    db,
    debug_toolbar,
    flask_static_digest,
    login_manager,
    migrate, ma, pagination, images_and_videos, videos, images, rq
)


def create_app(config_object="sweet_cms.settings"):
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    configure_logger(app)
    jinja2_inject(app)
    configure_uploads(app, (images, videos, images_and_videos))
    return app


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    pagination.init_app(app, db)
    flask_static_digest.init_app(app)
    rq.init_app(app)
    if app.config['REVERSE_PROXY'] != 0:
        from flask_reverse_proxy_fix.middleware import ReverseProxyPrefixFix
        ReverseProxyPrefixFix(app)

    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    sweet_apps = get_sweet_apps()
    admin_app = None
    for sweet_app in sweet_apps:
        if sweet_app.name == 'Admin':
            admin_app = sweet_app
        else:
            app.register_blueprint(sweet_app.app_module.views.blueprint, url_prefix=sweet_app.prefix)
    if admin_app:
        for sweet_app in sweet_apps:
            if sweet_app != admin_app and sweet_app.name == 'Eventy':
                # try:
                    sweet_app.app_module.admin.register_routes(admin_app.app_module.views.blueprint)
                # except:
                #     pass
        app.register_blueprint(admin_app.app_module.views.blueprint, url_prefix=admin_app.prefix)
    return None


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template(f"{error_code}.html"), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"db": db, "User": user.models.User}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)


def configure_logger(app):
    """Configure loggers."""
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)


def jinja2_inject(app):
    @app.context_processor
    def inject_date():
        from datetime import datetime
        return dict(today=datetime.now())

    @app.context_processor
    def themed():
        return dict(themed=themed_template)
