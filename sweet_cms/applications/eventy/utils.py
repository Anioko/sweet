import json
import os
import base64
import errno
import re

from sweet_cms.extensions import db


def ensure_dir_exists(dir_path):
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def save_base64file(file_path, file_name, data):
    ensure_dir_exists(file_path)
    file_full_path = os.path.join(file_path, file_name)
    data = ','.join(data.split(',')[1:])
    data = bytes(data, 'utf-8')
    with open(file_full_path, "wb") as fh:
        fh.write(base64.decodebytes(data))


def save_base64video(video_upload_path, file_name, data):
    ensure_dir_exists(video_upload_path)
    file_full_path = os.path.join(video_upload_path, file_name)
    with open(file_full_path, 'wb+') as destination:
        for chunk in data.chunks():
            destination.write(chunk)


def m3u8_fix(file_path, prefix):
    if os.path.exists(file_path):
        file_dir = os.path.dirname(file_path)
        reader = open(file_path, 'r')
        original_text = reader.read()
        new_text = ""
        reader.close()
        for line in original_text.splitlines():
            if '.m3u8' in line:
                new_line = os.path.join(prefix, line)
                new_play_list_path = os.path.join(file_dir, line)
                m3u8_fix(new_play_list_path, prefix)
            elif '.ts' in line:
                new_line = os.path.join(prefix, line)
            else:
                new_line = line
            new_text = new_text + new_line + "\n"
        writer = open(file_path, 'w')
        writer.write(new_text)
        writer.close()


def process_video(file_id, **kwargs):
    from sweet_cms.models import ProgrammeFile
    from libs.sweet_apps import get_sweet_app
    from autoapp import app
    import ffmpeg_streaming
    from ffmpeg_streaming import Formats
    import ffmpeg
    from shutil import copy
    from flask import url_for

    with app.app_context():
        eventy_app = get_sweet_app('Eventy')
        programme_file = ProgrammeFile.query.filter_by(id=file_id).first()
        if not programme_file:
            print("File Was deleted , stopping now")
            return
        file_path = programme_file.file_url
        app.config['SERVER_NAME'] = 'localhost'
        file_url = '/admin/eventy/uploads/programmes/{}/videos/'.format(programme_file.programme.id)
        file_path = os.path.join(eventy_app.app_path, app.config['EVENTY_UPLOADS_DIR'], file_path)
        print(file_id, programme_file, file_path, file_url)

        if os.path.exists(file_path):
            programme_file.file_status = 'processing'
            db.session.add(programme_file)
            db.session.commit()

            file_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            bare_file_name = '.'.join(file_name.split('.')[:-1])
            new_path = os.path.join(file_dir, bare_file_name+'.mp4')
            # data = ffmpeg.probe(file_path)
            input_video = ffmpeg.input(file_path)
            output_path = os.path.join('/tmp', bare_file_name+'.mp4')
            (
                ffmpeg
                    .output(input_video, output_path, vcodec='libx264', acodec='aac', movflags='faststart')
                    .overwrite_output()
                    .run()
            )
            copy(output_path, file_dir)
            # os.remove(output_path)
            if new_path != file_path:
                os.remove(file_path)
            # if "bit_rate" not in str(data):
            #     (
            #         ffmpeg
            #             .output(input_video, output_path, vcodec='copy', acodec='copy')
            #             .overwrite_output()
            #             .run()
            #     )
            #     copy(output_path, file_path)
            #     os.remove(output_path)
            # video = ffmpeg_streaming.input(file_path)
            # hls = video.hls(Formats.h264())
            # hls.auto_generate_representations()
            # hls.output(playlist_path)
            # m3u8_fix(playlist_path, file_url)
            data = ffmpeg.probe(new_path)
            programme_file.file_details = json.dumps(data)
            programme_file.file_status = 'ready'
            programme_file.file_name = bare_file_name+'.mp4'
            db.session.add(programme_file)
            db.session.commit()
            print("Done on : {}".format(str(file_path)))


def fire_programme_start(programme_id, **kwargs):
    import datetime
    from sweet_cms.models import Programme
    from libs.sweet_apps import get_sweet_app
    from autoapp import app
    import socketio
    with app.app_context():
        programme = Programme.query.filter_by(id=programme_id).first()
        if not programme:
            print("Programme Was deleted , stopping now")
            return
        if not app.config['DEBUG']:
            ws_url = "https://www.mediville.com"
            path = 'sockets/socket.io'
        else:
            ws_url = "http://127.0.0.1:5501"
            path = "socket.io"
        sio = socketio.Client()
        sio.connect(ws_url, socketio_path=path)
        sio.emit("programme_started", {"event_id": programme.event.id, "programme_id": programme.id})
        print("HI", datetime.datetime.now())
