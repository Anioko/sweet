import datetime

from flask import request
from flask_restful import Resource

from sweet_cms.decorators import api_route, admin_required


@api_route("/eventy/event/add", 'eventy_event_add')
class EventAdd(Resource):

    @admin_required
    def post(self):
        from sweet_cms.forms import CreateEventForm
        from sweet_cms.models import Event, EventSchema
        from flask_login import current_user
        from sweet_cms.extensions import db
        from slugify import slugify
        import time

        form = CreateEventForm(request.form)
        if form.validate():
            slug = slugify(form.name.data)
            check_event = Event.query.filter_by(slug=slug).first()
            if check_event:
                slug = slugify(form.name.data + " " + str(int(time.time())))
            event = Event.create(
                name=form.name.data,
                slug=slug,
                description=form.description.data,
                start_time=form.start_time.data + datetime.timedelta(minutes=int(form.offset.data)),
                end_time=form.end_time.data + datetime.timedelta(minutes=int(form.offset.data)),
                user=current_user
            )
            db.session.add(event)
            db.session.commit()
            return {
                'status': 1
            }
        else:
            return {
                'status': 0,
                'errors': form.errors
            }


@api_route("/eventy/events/list", 'eventy_events_list')
class GetEvents(Resource):

    @admin_required
    def get(self):
        from sweet_cms.models import Event, EventSchema
        from flask_login import current_user
        from sweet_cms.extensions import pagination
        schema = EventSchema()
        events = pagination.paginate(current_user.events, schema, True)
        return {
            'status': 1,
            'events': events
        }


@api_route("/eventy/programme/add", 'eventy_programme_add')
class ProgrammeAdd(Resource):

    @admin_required
    def post(self):
        from sweet_cms.forms import CreateProgrammeForm
        from sweet_cms.models import Event, EventSchema, Programme, ProgrammeSchema
        from sweet_cms.extensions import db, rq
        from sweet_cms.utils import fire_programme_start

        form = CreateProgrammeForm(request.form)
        event_id = request.form.get('event_id')
        if not event_id:
            return {
                'status': 0,
                'errors': {'name': "Something went wrong please try again later"}
            }
        event = Event.query.filter_by(id=event_id).first()
        if not event:
            return {
                'status': 0,
                'errors': {'name': "Something went wrong please try again later"}
            }
        if form.validate():
            for prog in event.programmes:
                if form.start_time.data + datetime.timedelta(minutes=int(form.offset.data)) < prog.end_time:
                    return {
                        'status': 0,
                        'errors': {'start_time': ["You cannot start a programme at this time, because the programme '{}' would still be running".format(prog.name)]}
                    }

            programme = Programme.create(
                name=form.name.data,
                description=form.description.data,
                start_time=form.start_time.data + datetime.timedelta(minutes=int(form.offset.data)),
                end_time=form.end_time.data + datetime.timedelta(minutes=int(form.offset.data)),
                programme_type=form.programme_type.data,
                event_id=event_id
            )
            db.session.add(programme)
            db.session.commit()
            db.session.refresh(programme)
            data = rq.get_queue().enqueue_at(programme.start_time, fire_programme_start, programme_id=programme.id)
            programme.job_id = str(data.id)
            db.session.add(programme)
            db.session.commit()
            return {
                'status': 1
            }
        else:
            return {
                'status': 0,
                'errors': form.errors
            }


@api_route("/eventy/event/<string:event_slug>/stream", 'eventy_event_stream')
class GetEventStream(Resource):

    def get(self, event_slug):
        from sweet_cms.models import Event, EventSchema, Programme, ProgrammeFile
        import datetime
        from flask_login import current_user
        from sweet_cms.extensions import pagination
        from flask import url_for

        event = Event.query.filter_by(slug=event_slug).first()
        if not event:
            return {
                'status': 0
            }
        programme_streaming = event.programmes.filter(Programme.end_time >= datetime.datetime.now()).first()
        if not programme_streaming:
            return {
                'status': 2
            }
        videos = programme_streaming.files.filter_by(file_type='video').filter_by(file_status='ready').order_by(ProgrammeFile.view_order).all()
        if not videos:
            return {
                'status': 3
            }
        current_stream_time = datetime.datetime.now() - programme_streaming.start_time
        current_stream_time = float(current_stream_time.total_seconds())
        if current_stream_time < 0:
            return {
                'status': 4
            }
        collective_duration = 0
        video_to_play = None
        for video in videos:
            collective_duration += video.video_duration
            if collective_duration >= current_stream_time:
                video_to_play = video
                break
        if not video_to_play:
            return {
                'status': 4
            }
        video_url = url_for('admin.eventy_uploaded', file_path=video_to_play.file_url, _external=True, _scheme='https')
        current_duration = current_stream_time - collective_duration + video_to_play.video_duration
        return {
            'status': 1,
            'stream_url': video_url,
            'current_duration': current_duration
        }
