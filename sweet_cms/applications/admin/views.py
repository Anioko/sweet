from flask import Blueprint, render_template, request, url_for, redirect, current_app, flash
from flask_login import login_user

from libs.sweet_apps import get_sweet_apps
from libs.sweet_theming import render_themed_template, themed_template
from sweet_cms.applications.admin.forms import AdminLoginForm
from sweet_cms.decorators import anonymous_required, admin_required
from sweet_cms.forms import UserCrudForm

blueprint = Blueprint("admin", __name__, static_folder="./static", template_folder='templates')


@blueprint.app_context_processor
def handle_sweet_app_includes():
    sweet_apps = get_sweet_apps()
    return dict(sweet_apps=sweet_apps)


@blueprint.route('/')
@admin_required
def index():
    return render_template(themed_template("index.html", 'admin'))


@blueprint.route("/login/", methods=["GET", "POST"])
@anonymous_required
def login():
    form = AdminLoginForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            login_user(form.user)
            # sync_cart()
            redirect_url = url_for("admin.index")
            return redirect(redirect_url)
    return render_template(themed_template("login.html", 'admin'), form=form)


# ############### CRUD ################


# Admins CRUD
@blueprint.route("/admins/", defaults={"page": 1})
@blueprint.route("/admins/<int:page>")
@admin_required
def admin_list(page):
    from sweet_cms.models import User

    admins = User.query.filter_by(is_admin=True).paginate(page, per_page=40)
    return render_template(themed_template("admins/admins_list.html", theme_type='admin'), admins=admins)


@blueprint.route("/admins/add_admin/", methods=["GET", "POST"])
@admin_required
def admin_add():
    from sweet_cms.models import User

    form = UserCrudForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            User.create(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                password=form.password.data,
                active=True,
                is_admin=True,
            )
            flash("Admin Added Successfully .", "success")
            return redirect(url_for("admin.admin_list"))
    return render_template(themed_template("admins/admins_add.html", 'admin'),form=form)


@blueprint.route("/admins/update/<int:admin_id>/", methods=["GET", "POST"])
@admin_required
def admin_update(admin_id):
    from sweet_cms.models import User

    admin = User.query.get_or_404(admin_id)
    form = UserCrudForm(obj=admin)
    form.password.validators = form.password.validators[1:]
    form.password.validators.insert(0, Optional())
    form.password.flags.required = False
    form.confirm.validators = form.confirm.validators[1:]
    form.confirm.validators.insert(0, Optional())
    form.confirm.flags.required = False

    if request.method == 'POST':
        if form.validate_on_submit():
            admin.username = form.username.data
            admin.email = form.email.data
            admin.first_name = form.first_name.data
            admin.last_name = form.last_name.data
            if form.password.data:
                admin.set_password(form.password.data)
            db.session.add(admin)
            db.session.commit()
            flash("Admin Updated Successfully", "success")
            return redirect(url_for('admin.admin_list'))
    return render_template("admin/admins/admins_update.html", admin=admin, form=form)


@blueprint.route("/admins/delete/<int:admin_id>/", methods=["POST"])
@admin_required
def admin_delete(admin_id):
    from sweet_cms.models import User

    if admin_id == 0:  # bulk delete
        admin_ids = request.form.get('ids[]').split(',')
        admins = User.query.filter(User.id.in_(admin_ids)).all()
    else:
        admins = [User.query.get_or_404(admin_id)]
    for admin in admins: db.session.delete(admin)
    db.session.commit()
    flash("Admins Deleted Successfully", "success")
    return redirect(url_for('admin.admin_list'))


# Clients CRUD
@blueprint.route("/users/", defaults={'page': 1})
@blueprint.route("/users/<int:page>")
@admin_required
def user_list(page):
    from sweet_cms.models import User

    users = User.query.filter_by(is_admin=False).paginate(page, per_page=40)
    return render_template("admin/users/users_list.html", users=users)


@blueprint.route("/users/add_user/", methods=["GET", "POST"])
@admin_required
def user_add():
    from sweet_cms.models import User

    form = UserCrudForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            User.create(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                password=form.password.data,
                active=True,
                is_admin=False,
            )
            flash("Client Added Successfully .", "success")
            return redirect(url_for("admin.user_list"))
    return render_template("admin/users/users_add.html", form=form)


@blueprint.route("/users/update/<int:user_id>/", methods=["GET", "POST"])
@admin_required
def user_update(user_id):
    from sweet_cms.models import User

    user = User.query.get_or_404(user_id)
    form = UserCrudForm(obj=user)
    form.password.validators = form.password.validators[1:]
    form.password.validators.insert(0, Optional())
    form.password.flags.required = False
    form.confirm.validators = form.confirm.validators[1:]
    form.confirm.validators.insert(0, Optional())
    form.confirm.flags.required = False

    if request.method == 'POST':
        if form.validate_on_submit():
            user.username = form.username.data
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            if form.password.data:
                user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Client Updated Successfully", "success")
            return redirect(url_for('admin.user_list'))

    return render_template("admin/users/users_update.html", user=user, form=form)


@blueprint.route("/users/delete/<int:user_id>/", methods=["POST"])
@admin_required
def user_delete(user_id):
    from sweet_cms.models import User

    if user_id == 0:  # bulk delete
        user_ids = request.form.get('ids[]').split(',')
        users = User.query.filter(User.id.in_(user_ids)).all()
    else:
        users = [User.query.get_or_404(user_id)]
    for user in users: db.session.delete(user)
    db.session.commit()
    flash("Clients Deleted Successfully", "success")
    return redirect(url_for('admin.user_list'))


#  Modules CRUD
@blueprint.route("/modules/", defaults={'page': 1})
@blueprint.route("/modules/<int:page>")
@admin_required
def module_list(page):
    modules = Module.query.paginate(page, per_page=40)
    return render_template("admin/modules/modules_list.html", modules=modules)


@blueprint.route('/modules/add_module', methods=['GET', 'POST'])
@admin_required
def module_add():
    form = ModuleCrudForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            image = images.save(request.files['image'])
            module = Module.create(
                name=form.name.data,
                description=form.description.data,
                demo_url=form.demo_url.data,
                code_path=form.code_path.data,
                price=form.price.data,
                support_price=form.support_price.data,
                image_filename=image
            )
            db.session.add(module)
            db.session.commit()
            db.session.refresh(module)
            for image in request.files.getlist('images'):
                image_filename = images.save(image)
                ModuleImage.create(
                    module=module,
                    image_filename=image_filename
                )
            flash("Module Added Successfully .", "success")
            return redirect(url_for("admin.module_list"))
    return render_template("admin/modules/modules_add.html", form=form)


@blueprint.route('/modules/update_module/<int:module_id>', methods=['GET', 'POST'])
@admin_required
def module_update(module_id):
    module = Module.query.get_or_404(module_id)
    form = ModuleCrudForm(obj=module)
    form.images.validators = form.images.validators[1:]
    form.images.validators.insert(0, Optional())
    form.images.flags.required = False
    form.image.validators = form.image.validators[1:]
    form.image.validators.insert(0, Optional())
    form.image.flags.required = False

    if request.method == 'POST':
        if form.validate_on_submit():
            module.name = form.name.data
            module.description = form.description.data
            module.demo_url = form.demo_url.data
            module.code_path = form.code_path.data
            module.price = form.price.data
            module.support_price = form.support_price.data
            module.long_description = form.long_description.data
            module.tags = form.tags.data
            module.release_date = form.release_date.data
            module.last_update_date = form.last_update_date.data
            if request.files['image']:
                image = images.save(request.files['image'])
                if os.path.exists(module.image_path):
                    os.remove(module.image_path)
                module.image_filename = image
            db.session.add(module)
            db.session.commit()
            try:
                image_ids = request.form.getlist('old_images[]')
            except:
                image_ids = []
            for image in module.images:
                if str(image.id) not in image_ids:
                    if os.path.exists(image.image_path):
                        os.remove(image.image_path)
                    db.session.delete(image)
            if request.files['images']:
                for image in request.files.getlist('images'):
                    image_filename = images.save(image)
                    module_image = ModuleImage.create(
                        module=module,
                        image_filename=image_filename
                    )
                    db.session.add(module_image)
            db.session.commit()
            flash("Module Updated Successfully", "success")
            return redirect(url_for('admin.module_list'))

    return render_template("admin/modules/modules_update.html", module=module, form=form)


@blueprint.route('/modules/delete_module/<int:module_id>', methods=['GET', 'POST'])
@admin_required
def module_delete(module_id):
    if module_id == 0:  # bulk delete
        module_ids = request.form.get('ids[]').split(',')
        modules = Module.query.filter(Module.id.in_(module_ids)).all()
    else:
        modules = [Module.query.get_or_404(module_id)]
    for module in modules: db.session.delete(module)
    db.session.commit()
    flash("Modules Deleted Successfully", "success")
    return redirect(url_for('admin.module_list'))


# SlideShow CRUD
@blueprint.route("/slideshows/", defaults={'page': 1})
@blueprint.route("/slideshows/<int:page>")
@admin_required
def slideshow_list(page):
    slideshows = SlideShowImage.query.paginate(page, per_page=40)
    return render_template("admin/slideshows/slideshows_list.html", slideshows=slideshows)


@blueprint.route('/slideshows/add_slideshow', methods=['GET', 'POST'])
@admin_required
def slideshow_add():
    form = SlideShowCrudForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            title = form.title.data
            image = images.save(request.files['image'])
            slideshow = SlideShowImage(title=title, image_filename=image)
            db.session.add(slideshow)
            db.session.commit()
            flash("SlideShow Added Successfully .", "success")
            return redirect(url_for("admin.slideshow_list"))

    return render_template("admin/slideshows/slideshows_add.html", form=form)


# SOmething is Wrong Here
@blueprint.route('/slideshows/slideshow_update/<int:slideshow_id>', methods=['GET', 'POST'])
@admin_required
def slideshow_update(slideshow_id):
    slideshow = SlideShowImage.query.get(slideshow_id)
    form = SlideShowCrudForm(obj=slideshow)
    form.image.validators = form.image.validators[1:]
    form.image.validators.insert(0, Optional())
    form.image.flags.required = False
    if request.method == 'POST':
        if form.validate_on_submit():
            title = form.title.data
            slideshow.title = title
            if request.files['image']:
                image = images.save(request.files['image'])
                if os.path.exists(slideshow.image_path):
                    os.remove(slideshow.image_path)
                slideshow.image_filename = image
            db.session.add(slideshow)
            db.session.commit()
            flash("SlideShow Updated Successfully .", "success")
            return redirect(url_for("admin.slideshow_list"))

    return render_template('admin/slideshows/slideshows_update.html', form=form, slideshow=slideshow)


@blueprint.route('/slideshows/delete_slideshow/<int:slideshow_id>', methods=['GET', 'POST'])
@admin_required
def slideshow_delete(slideshow_id):
    if slideshow_id == 0:  # bulk delete
        slideshows_ids = request.form.get('ids[]').split(',')
        slideshows = SlideShowImage.query.filter(SlideShowImage.id.in_(slideshows_ids)).all()
    else:
        slideshows = [SlideShowImage.query.get_or_404(slideshow_id)]
    for slideshow in slideshows: db.session.delete(slideshow)
    db.session.commit()
    flash("SlideShows Deleted Successfully", "success")
    return redirect(url_for('admin.slideshow_list'))


# SEO CRUD
@blueprint.route("/seo/", defaults={'page': 1})
@blueprint.route("/seo/<int:page>")
@admin_required
def seo_list(page):
    seos = Seo.query.paginate(page, per_page=40)
    return render_template("admin/seos/seos_list.html", seos=seos)


@blueprint.route('/seos/add_seo', methods=['GET', 'POST'])
@admin_required
def seo_add():
    form = SeoCrudForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            Seo.create(
                meta_tag=form.meta_tag.data,
                title=form.title.data,
                content=form.content.data,
            )

            flash("SEO Famous Words Added Successfully .", "success")
            return redirect(url_for("admin.seo_list"))
    return render_template('admin/seos/seos_add.html', form=form)


@blueprint.route('/seos/update_seo/<int:seo_id>', methods=['GET', 'POST'])
@admin_required
def seo_update(seo_id):
    seo = Seo.query.get_or_404(seo_id)
    form = SeoCrudForm(obj=seo)
    if request.method == 'POST':
        if form.validate_on_submit():
            seo.meta_tag = form.meta_tag.data
            seo.title = form.title.data
            seo.content = form.content.data
            db.session.add(seo)
            db.session.commit()
            flash("SEO Words/Tags Updated Successfully", "success")
            return redirect(url_for('admin.seo_list'))

    return render_template("admin/seos/seos_update.html", seo=seo, form=form)


@blueprint.route('/seos/delete_seo/<int:seo_id>', methods=['GET', 'POST'])
@admin_required
def seo_delete(seo_id):
    if seo_id == 0:  # bulk delete
        seo_ids = request.form.get('ids[]').split(',')
        seos = Seo.query.filter(Seo.id.in_(seo_ids)).all()
    else:
        seos = [Seo.query.get_or_404(seo_id)]
    for seo in seos: db.session.delete(seo)
    db.session.commit()
    flash("SEO words  Deleted Successfully", "success")
    return redirect(url_for('admin.seo_list'))


@blueprint.route('/settings', methods=['GET', 'POST'])
def settings():
    available_settings = current_app.config['AVAILABLE_ADMIN_SETTINGS']
    available_settings_keys = [key[0] for key in available_settings]
    settings_objects = Setting.query.filter(Setting.name.in_(available_settings_keys)).all()
    current_app.logger.info(available_settings_keys)
    current_app.logger.info(settings_objects)
    if len(settings_objects) != len(available_settings):
        for setting in available_settings:
            get_setting_val(setting)
        settings_objects = Setting.query.filter(Setting.name.in_(available_settings_keys)).all()
    if request.method == 'POST':
        for setting in available_settings:
            setting_obj = get_setting_val(setting)
            setting_val = request.form.get(setting[0])
            if not setting_val:
                flash("Wrong value for {}".format(setting[1]), 'danger')
                return redirect(url_for('admin.settings'))
            setting_obj.value = setting_val
            db.session.add(setting_obj)
        db.session.commit()
        flash("Settings updated successfully", 'success')
        return redirect(url_for('admin.settings'))
    current_app.logger.info(settings_objects)
    return render_template('admin/settings.html', settings=settings_objects)
