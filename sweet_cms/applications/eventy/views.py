import os

from flask import Blueprint, render_template, Response

from libs.sweet_theming import themed_template

blueprint = Blueprint("eventy", __name__, static_folder="./static", template_folder='templates')


@blueprint.route('/event/<string:event_slug>')
def event(event_slug):
    from sweet_cms.models import Event

    event = Event.query.filter_by(slug=event_slug).first_or_404()
    return render_template(themed_template('eventy/event.html', 'web'), event=event)


@blueprint.route('/event/stream/<event_slug>')
def event_stream(event_slug):
    from sweet_cms.models import Programme, Event
    import datetime
    from libs.sweet_apps import get_sweet_app
    from flask import current_app
    eventy_app = get_sweet_app('Eventy')
    event = Event.query.filter_by(slug=event_slug).first()
    stream_playlist = ""
    if event:
        current_app.logger.info("Found Event {}".format(event.id))
        programme_streaming = event.programmes.filter(Programme.end_time >= datetime.datetime.now()).first()
        if programme_streaming:
            current_app.logger.info("Found Programme {}".format(programme_streaming.id))
            videos = programme_streaming.videos
            if videos:
                current_app.logger.info("Found {} Videos".format(len(videos)))
                video_streaming = videos[0]
                if video_streaming.file_status == 'ready':
                    current_app.logger.info("Found video {}".format(programme_streaming.id))
                    file_path = video_streaming.file_url
                    file_path = os.path.join(eventy_app.app_path, current_app.config['EVENTY_UPLOADS_DIR'], file_path)
                    file_dir = os.path.dirname(file_path)
                    file_name = os.path.basename(file_path)
                    bare_file_name = '.'.join(file_name.split('.')[:-1])
                    playlist_path = os.path.join(file_dir, f"{bare_file_name}.m3u8")
                    current_app.logger.info("Found playlist {}".format(playlist_path))
                    stream_playlist = open(playlist_path).read()
                    return Response(stream_playlist,
                                    mimetype='application/x-mpegURL')
    return Response(stream_playlist,
                    mimetype='application/x-mpegURL')
