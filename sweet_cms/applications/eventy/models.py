import os

from sweet_cms.database import PkModel, Column
from sweet_cms.extensions import db, ma


class Event(PkModel):
    __tablename__ = "events"
    name = Column(db.String(80), nullable=False)
    description = Column(db.String(256), nullable=False)
    slug = Column(db.String(256), nullable=False, unique=True)
    start_time = Column(db.DateTime, server_default=db.text('current_timestamp'), default=db.func.now(), nullable=False)
    end_time = Column(db.DateTime, server_default=db.text('current_timestamp'), default=db.func.now(), nullable=True)
    user_id = Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=True, default=None)
    user = db.relationship("User", backref=db.backref("events", lazy='dynamic'))


class EventManager(PkModel):
    __tablename__ = "event_managers"
    user_id = Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=True, default=None)
    event_id = Column(db.Integer, db.ForeignKey('events.id', ondelete="CASCADE"), nullable=True, default=None)
    user = db.relationship("User", backref=db.backref("managements"))
    event = db.relationship("Event", backref=db.backref("managers"))


class Programme(PkModel):
    __tablename__ = "event_programmes"
    event_id = Column(db.Integer, db.ForeignKey('events.id', ondelete="CASCADE"), nullable=True, default=None)
    name = Column(db.String(80), nullable=False)
    description = Column(db.String(256), nullable=False)
    start_time = Column(db.DateTime, server_default=db.text('current_timestamp'), default=db.func.now(), nullable=False)
    end_time = Column(db.DateTime, server_default=db.text('current_timestamp'), default=db.func.now(), nullable=False)
    programme_type = Column(db.String(80), nullable=False)
    job_id = Column(db.String(100), nullable=True)
    event = db.relationship("Event", backref=db.backref("programmes", lazy="dynamic"))

    @property
    def videos(self):
        return self.files.filter_by(file_type='video').order_by(ProgrammeFile.view_order).all()

    @property
    def banners(self):
        return self.files.filter_by(file_type='banner').order_by(ProgrammeFile.view_order).all()


class ProgrammeFile(PkModel):
    __tablename__ = "programme_files"
    programme_id = Column(db.Integer, db.ForeignKey('event_programmes.id', ondelete="CASCADE"), nullable=True, default=None)
    file_type = Column(db.String(80), nullable=False)
    file_status = Column(db.String(80), nullable=False, default='in queue', server_default=db.text('in queue'))
    file_details = Column(db.Text, nullable=True)
    file_name = Column(db.String(256), nullable=False)
    view_order = Column(db.Integer, default=0, server_default=db.text('0'))
    programme = db.relationship("Programme", backref=db.backref("files", lazy='dynamic'))

    @property
    def file_url(self):
        return os.path.join('programmes', str(self.programme_id), 'images' if self.file_type == 'banner' else 'videos', self.file_name)

    @property
    def file_path(self):
        from libs.sweet_apps import get_sweet_app
        from flask import current_app
        eventy_app = get_sweet_app('Eventy')
        return os.path.join(eventy_app.app_path, current_app.config['EVENTY_UPLOADS_DIR'], self.file_url)

    @property
    def video_duration(self):
        import json
        try:
            return float(json.loads(self.file_details)['format']['duration'])
        except:
            return None


class ProgrammeSchema(ma.Schema):
    class Meta:
        model = Programme
        fields = ("id", "name", "description", "start_time", "end_time", "programme_type")


class EventSchema(ma.Schema):
    class Meta:
        model = Event
        fields = ("id", "name", "description", "start_date", "end_date", "programmes", "slug")
    programmes = ma.Nested(ProgrammeSchema, many=True)
