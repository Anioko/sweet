"""Admin forms."""
import sys

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import PasswordField, StringField, FloatField, MultipleFileField, FileField, SelectField, DateField, \
    TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired
from wtforms_alchemy import Unique, ModelForm, model_form_factory

from flask_uploads import UploadSet, IMAGES

images = UploadSet('images', IMAGES)
BaseModelForm = model_form_factory(FlaskForm)

# open('log', 'w').write(str(sys.modules))
# if "sweet_cms.models.User" not in sys.modules:
#     from sweet_cms.models import User


class AdminLoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(AdminLoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        from sweet_cms.models import User
        """Validate the form."""
        initial_validation = super(AdminLoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(username=self.username.data).first()
        
        if not self.user:
            self.username.errors.append("Unknown username")
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append("Invalid password")
            return False

        if not self.user.active:
            self.username.errors.append("User not activated")
            return False
        return True


class UserCrudForm(BaseModelForm):
    """Client Form ."""
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=25), Unique("User.username")])
    first_name = StringField("First Name", validators=[ Length(min=3, max=40)])
    last_name = StringField("Last Name", validators=[ Length(min=3, max=40)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(min=6, max=40), Unique("User.email")])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=40)])
    confirm = PasswordField("Verify password",[DataRequired(), EqualTo("password", message="Passwords must match")])


class ModuleCrudForm(BaseModelForm):
    """Client Form ."""
    name = StringField("Name", validators=[DataRequired(), Length(min=5, max=80)])
    description = StringField("Description", validators=[DataRequired(), Length(min=5, max=256)])
    long_description = TextAreaField("Long Description", validators=[DataRequired(), Length(min=5)])
    tags = StringField("Tags (comma separated)", validators=[DataRequired(), Length(min=5)])
    demo_url = StringField("Demo Url", validators=[DataRequired(), Length(min=5, max=256)])
    code_path = StringField("Code Path", validators=[DataRequired(), Length(min=5, max=256)])
    price = FloatField("Price", validators=[DataRequired()])
    support_price = FloatField("Support Price", validators=[DataRequired()])
    release_date = DateField("Release Date", validators=[DataRequired()])
    last_update_date = DateField("Release Date", validators=[DataRequired()])
    image = FileField('Product Image (397x306)', validators=[FileRequired(), FileAllowed(images, 'Images only allowed!')])
    images = MultipleFileField('Product Screenshots (726x403)', validators=[DataRequired(), FileAllowed(images, 'Images only!')])


class SlideShowCrudForm(BaseModelForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=5, max=80)])
    image = FileField('SlideShow Image (928x413)', validators=[FileRequired(), FileAllowed(images, 'Images only allowed!')])


class SeoCrudForm(BaseModelForm):
    meta_tag = SelectField(u'Meta Tag',choices=[('name','name'),('property','property')] ,validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired(), Length(min=5, max=80)])
    content = StringField("Content", validators=[DataRequired(), Length(min=5, max=255)])
