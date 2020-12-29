from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, SelectField, FileField, HiddenField
from wtforms.fields.html5 import DateField, DateTimeLocalField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from wtforms_alchemy import model_form_factory

from sweet_cms.extensions import images_and_videos

BaseModelForm = model_form_factory(FlaskForm)


class CreateEventForm(BaseModelForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=5, max=80)])
    description = StringField("Description", validators=[DataRequired(), Length(min=5, max=256)])
    start_time = DateTimeLocalField("Start Time", validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    end_time = DateTimeLocalField("End Time", validators=[Optional()], format='%Y-%m-%dT%H:%M')
    offset = HiddenField('Time Offset')

    def validate_start_time(form, field):
        import datetime
        if field.data + datetime.timedelta(minutes=int(form.offset.data)) < datetime.datetime.now():
            raise ValidationError("Start Date must be in the future.")
        if form.end_time:
            if field.data > form.end_time.data:
                raise ValidationError("End Date must not be earlier than start date.")

    def validate_end_time(form, field):
        import datetime
        if field:
            if field.data + datetime.timedelta(minutes=int(form.offset.data)) < datetime.datetime.now():
                raise ValidationError("End date must be in the future.")


class CreateProgrammeForm(BaseModelForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=5, max=80)])
    description = StringField("Description", validators=[DataRequired(), Length(min=5, max=256)])
    start_time = DateTimeLocalField("Start Time", validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    end_time = DateTimeLocalField("End Time", validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    offset = HiddenField('Time Offset')
    programme_type = SelectField("Programme Type", choices=[('live', "Live Streaming"), ('videos', "Videos")])

    def validate_start_time(form, field):
        import datetime
        if field.data + datetime.timedelta(minutes=int(form.offset.data)) < datetime.datetime.now():
            raise ValidationError("Start time must be in the future.")
        elif field.data > form.end_time.data:
            raise ValidationError("End time must not be earlier than start time.")

    def validate_end_time(form, field):
        import datetime
        if field.data + datetime.timedelta(minutes=int(form.offset.data)) < datetime.datetime.now():
            raise ValidationError("End time must be in the future.")


class ProgrammeFileForm(BaseModelForm):
    file_type = SelectField("Data Type", choices=[('banner', "Programme Banner"), ('video', "Video File")])
    file_name = FileField('Upload File', validators=[FileAllowed(images_and_videos, 'Only Images & Videos only allowed!'), Optional()])
    view_order = IntegerField('View Order', validators=[DataRequired()])
