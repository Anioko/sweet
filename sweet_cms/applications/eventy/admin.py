from flask import render_template, abort, current_app, request, redirect, url_for, flash, send_from_directory, send_file
from flask_login import current_user

from libs.sweet_theming import themed_template
from sweet_cms.decorators import admin_required
from sweet_cms.extensions import db


def register_routes(blueprint):
    from sweet_cms.forms import CreateEventForm, CreateProgrammeForm, ProgrammeFileForm
    from sweet_cms.models import Programme, ProgrammeFile
    from libs.sweet_apps import get_sweet_app
    import os
    import time
    from sweet_cms.utils import flash_errors, save_base64file, save_base64video, process_video, ensure_dir_exists
    from sweet_cms.extensions import rq

    eventy_app = get_sweet_app('Eventy')

    @blueprint.route('/eventy/events')
    @admin_required
    def events():
        form = CreateEventForm()
        programme_form = CreateProgrammeForm()
        return render_template(themed_template('eventy/index.html', 'admin'), form=form, programme_form=programme_form)

    @blueprint.route('/eventy/programme/<int:programme_id>')
    @admin_required
    def events_programme_view(programme_id):
        import datetime
        from sweet_cms.utils import fire_programme_start

        programme = Programme.query.get_or_404(programme_id)
        # rq.get_queue().enqueue(
        #     process_video,
        #     file_id=24
        # )
        # programme_file = ProgrammeFile.query.get_or_404(12)
        # current_app.logger.info(programme_file.file_url + programme_file.file_name)
        # now = datetime.datetime.now()
        # now_plus_2 = now + datetime.timedelta(seconds=10)
        # data = get_queue().enqueue_at(now_plus_2, fire_programme_start, programme_id=programme_id)
        # current_app.logger.info(str(type(data.id)))

        # get_queue().enqueue(
        #     process_video,
        #     file_id=programme.videos[0].id
        # )
        programme_form = CreateProgrammeForm(obj=programme)
        programme_form.programme_type.disabled = True
        programme_data_form = ProgrammeFileForm()
        if programme.event not in current_user.events.all():
            abort(404)
        return render_template(themed_template('eventy/programme.html', 'admin'), programme=programme, programme_form=programme_form,
                               programme_data_form=programme_data_form)

    @blueprint.route('/eventy/programme/<int:programme_id>/add_data', methods=['POST'])
    @admin_required
    def add_programme_data(programme_id):
        programme = Programme.query.get_or_404(programme_id)
        uploads_path = os.path.join(eventy_app.app_path, current_app.config['EVENTY_UPLOADS_DIR'], 'programmes', f'{programme.id}')
        # current_app.logger.info(current_app.config['EVENTY_UPLOADS_DIR'])
        # current_app.logger.info(request.form)
        form = ProgrammeFileForm()
        if form.validate_on_submit():
            file_type = form.file_type.data
            view_order = form.view_order.data
            check_file = programme.files.filter_by(file_type=file_type).filter_by(view_order=view_order).first()
            if check_file:
                flash("There is already a file with the same type and view order for this programme.", 'danger')
                return redirect(url_for('admin.events_programme_view', programme_id=programme_id))
            media_type = request.form['media_type']
            file_name = None
            if file_type == 'banner':
                img_upload_path = os.path.join(uploads_path, 'images')
                file_name = f"{programme.name}_{int(time.time())}.png"
                file_name = file_name.replace(' ', '_')
                if media_type == 'capture':
                    save_base64file(img_upload_path, file_name, request.form['capture_data'])
                else:
                    image = request.files["file_name"]
                    ensure_dir_exists(img_upload_path)
                    image.save(os.path.join(img_upload_path, file_name))
            elif file_type == 'video':
                video_upload_path = os.path.join(uploads_path, 'videos')
                if media_type == 'capture':
                    file_name = f"{programme.name}.{int(time.time())}.webm"
                    file_name = file_name.replace(' ', '_')
                    save_base64file(video_upload_path, file_name, request.form['capture_data'])
                else:
                    video = request.files["file_name"]
                    filename = video.filename
                    ext = '.' + filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                    file_name = f"{programme.name}_{int(time.time())}"+ext
                    file_name = file_name.replace(' ', '_')
                    ensure_dir_exists(video_upload_path)
                    video.save(os.path.join(video_upload_path, file_name))
            programme_file = ProgrammeFile.create(
                file_type=file_type,
                view_order=view_order,
                file_name=file_name,
                programme=programme
            )
            db.session.add(programme_file)
            db.session.commit()
            db.session.refresh(programme_file)
            rq.get_queue().enqueue(
                process_video,
                file_id=programme_file.id,
            )
            flash("Programme data added successfully", 'success')
            return redirect(url_for('admin.events_programme_view', programme_id=programme_id))
        else:
            flash_errors(form, 'danger')
            return redirect(url_for('admin.events_programme_view', programme_id=programme_id))

    @blueprint.route('/eventy/uploads/<path:file_path>')
    def eventy_uploaded(file_path):
        file_path = os.path.join(eventy_app.app_path, current_app.config['EVENTY_UPLOADS_DIR'], file_path)
        return send_file(file_path, conditional=True)

    @blueprint.route('/eventy/update_programme/<int:programme_id>', methods=['POST'])
    @admin_required
    def update_programme(programme_id):
        from sweet_cms.utils import fire_programme_start
        import datetime

        programme = Programme.query.get_or_404(programme_id)
        form = CreateProgrammeForm(request.form)
        create_job = programme.start_time != form.start_time.data
        if form.validate():
            programme.name = form.name.data
            programme.description = form.description.data
            programme.start_time = form.start_time.data + datetime.timedelta(minutes=int(form.offset.data))
            programme.end_time = form.end_time.data + datetime.timedelta(minutes=int(form.offset.data))
            if create_job:
                if programme.job_id:
                    rq.get_queue().remove(programme.job_id)
                data = rq.get_queue().enqueue_at(programme.start_time, fire_programme_start, programme_id=programme.id)
                programme.job_id = str(data.id)
            db.session.add(programme)
            db.session.commit()
            current_app.logger.info(str(programme.start_time))
            current_app.logger.info(str(type(programme.start_time)))
            flash("Programme updated successfully", 'success')
            return redirect(url_for('admin.events_programme_view', programme_id=programme_id))
        else:
            flash_errors(form, 'danger')
            return redirect(url_for('admin.events_programme_view', programme_id=programme_id))

    @blueprint.route('/eventy/programme/<int:programme_id>/delete_data/<int:programme_file_id>', methods=['POST'])
    @admin_required
    def delete_programme_data(programme_id, programme_file_id):
        programme = Programme.query.get_or_404(programme_id)
        programme_file = ProgrammeFile.query.filter_by(programme=programme).filter_by(id=programme_file_id).first()
        if not programme_file:
            abort(404)
        if os.path.exists(programme_file.file_path):
            os.remove(programme_file.file_path)
        db.session.delete(programme_file)
        db.session.commit()
        flash("Programme file deleted successfully", 'success')
        return redirect(url_for('admin.events_programme_view', programme_id=programme_id))

    @blueprint.route('/eventy/programme/<int:programme_id>/update_data/<int:programme_file_id>', methods=['POST'])
    @admin_required
    def update_programme_data(programme_id, programme_file_id):
        programme = Programme.query.get_or_404(programme_id)
        programme_file = ProgrammeFile.query.filter_by(programme=programme).filter_by(id=programme_file_id).first()
        if not programme_file:
            abort(404)
        view_order = request.form.get('view_order')
        if view_order:
            if view_order == '+1':
                target_order = programme_file.view_order + 1
            elif view_order == '-1':
                target_order = programme_file.view_order - 1
            target_file = ProgrammeFile.query.filter_by(programme=programme).filter_by(file_type=programme_file.file_type).filter_by(view_order=target_order).first()
            current_app.logger.info("{}, {}, {}, {}".format(programme_file.id, programme_file.view_order, str(target_file), target_order))
            current_order = programme_file.view_order
            programme_file.view_order = target_order
            target_file.view_order = current_order
            db.session.add(programme_file)
            db.session.add(target_file)
            db.session.commit()
        flash("Programme file order updated successfully", 'success')
        return redirect(url_for('admin.events_programme_view', programme_id=programme_id))
