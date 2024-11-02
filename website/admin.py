from flask import render_template, request, abort, redirect, url_for, jsonify, flash, Blueprint
from base64 import b64decode
from flask_login import login_required, current_user
from datetime import datetime
from . import models
from . import db
from .utils import save_image, delete_image, save_pdf

admin = Blueprint('admin', __name__)

@admin.route('/')
@admin.route('/home')
@login_required
def admin_home():
    user = current_user
    url = f'{request.host_url}{user.id}'
    return render_template('admin.html', user=user, url=url)


@admin.route('/add-organizer', methods=['POST'])
@login_required
def add_organizer():
    user_id = current_user.id
    name = request.form['name']
    short_name = request.form['short_name']
    logo_data = request.form['cropped_logo']

    if logo_data:
        header, data = logo_data.split(';base64,')
        logo = b64decode(data)  # This should be the binary image data

    print(f"Name: {name}, Short Name: {short_name}, Logo Data: {logo_data}")

    new_organizer = models.Organizer(name=name, user_id=user_id, short_name=short_name.lower(), logo=save_image(image_file=logo, destination='organizer'))

    db.session.add(new_organizer)
    db.session.commit()

    return jsonify({
        "success": True,
        "organizer": {
            "id": new_organizer.id,
            "user_id": new_organizer.user_id,
            "name": new_organizer.name,
            "short_name": new_organizer.short_name,
            "logo": new_organizer.logo
        }
    })

@admin.route('/add-event', methods=['GET', 'POST'])
@login_required
def add_event():
    user_id = current_user.id
    categories = models.Category.query.all()
    organizers = models.Organizer.query.filter_by(user_id=user_id)

    if request.method == 'POST':
        name = request.form.get('name')
        short_name = request.form.get('short_name')
        date = request.form.get('date')
        venue = request.form.get('venue')
        points = request.form.get('points')
        reflection = request.form.get('reflection')
        category_id = request.form.get('category_id')
        organizer_id = request.form.get('organizer_id')

        thumbnail_data = request.form['cropped_thumbnail']
        proof_data = request.form['cropped_proof']

        if not all([name, short_name, date, venue, points, reflection, category_id, organizer_id, thumbnail_data, proof_data]):
            flash("All fields are required.", category='error')

        if not all([name, short_name, date, venue, points, reflection, category_id, organizer_id]):
            flash("All fields are required.", category='error')

        if thumbnail_data:
            header, data = thumbnail_data.split(';base64,')
            thumbnail = b64decode(data)  # This should be the binary image data

        if proof_data:
            header, data = proof_data.split(';base64,')
            proof = b64decode(data)  # This should be the binary image data

        try:
            points = int(points)
        except ValueError:
            flash("Points must be an integer.", category='error')

        if points < 1 or points > 4:
            flash("Points must be from 1 to 4.", category='error')

        new_event = models.Event(
            name=name,
            short_name=short_name.lower(),
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            venue=venue,
            points=points,
            reflection=reflection,
            category_id=category_id,
            organizer_id=organizer_id,
            user_id=user_id,
            thumbnail=save_image(image_file=thumbnail, destination='thumbnail', max_size=(480, 270)),
            proof=save_image(image_file=proof, destination='proof', max_size=(720, 405))
        )

        db.session.add(new_event)
        db.session.commit()

        return redirect(url_for('admin.editable_events'))

    return render_template('event_form.html', categories=categories, organizers=organizers, user=current_user)

@admin.route('/edit-organizer')
@login_required
def editable_organizers():
    user_id = current_user.id
    organizers = models.Organizer.query.filter_by(user_id=user_id)

    if not organizers:
        flash("No organizers found.", category='error')

    return render_template('editable_organizers.html', organizers=organizers, user=current_user)

@admin.route('/edit-event')
@login_required
def editable_events():
    user_id = current_user.id
    events = models.Event.query.filter_by(user_id=user_id)

    if not events:
        flash("No events found.", category='error')

    return render_template('editable_events.html', events=events, user=current_user)

@admin.route('/edit-organizer/<organizer_id>', methods=['GET', 'POST'])
@login_required
def edit_organizer(organizer_id):
    organizer = models.Organizer.query.get(int(organizer_id))

    if not organizer:
        abort(404, description="Organizer not found.")

    if request.method == 'POST':
        name = request.form['name']
        short_name = request.form['short_name'].lower()
        logo_data = request.form.get('cropped_logo')

        if logo_data:
            header, data = logo_data.split(';base64,')
            logo = b64decode(data)  # This should be the binary image data
                # Save the image and update the organizer's logo
            organizer.logo = save_image(image_file=logo, destination='organizer', method='replace', prev_filename=organizer.logo)

        # Update other fields regardless of logo upload
        organizer.name = name
        organizer.short_name = short_name

        # Commit the changes to the database
        db.session.commit()
        return redirect(url_for('admin.editable_organizers'))

    return render_template('organizer_form.html', organizer=organizer, user=current_user)

@admin.route('/edit-event/<event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = models.Event.query.filter_by(id=event_id, user_id=current_user.id).first()
    categories = models.Category.query.all()
    organizers = models.Organizer.query.filter_by(user_id=current_user.id)

    if not event:
        abort(404, description="Event not found.")

    if request.method == 'POST':
        # Retrieve form data
        name = request.form['name']
        short_name = request.form['short_name']
        date = request.form['date']
        venue = request.form['venue']
        points = request.form['points']
        reflection = request.form['reflection']
        category_id = request.form['category_id']
        organizer_id = request.form['organizer_id']

        thumbnail_data = request.form['cropped_thumbnail']
        proof_data = request.form['cropped_proof']

        if not all([name, short_name, date, venue, points, reflection, category_id, organizer_id]):
            flash("All fields are required.", category='error')

        if thumbnail_data:
            header, data = thumbnail_data.split(';base64,')
            thumbnail = b64decode(data)  # This should be the binary image data
            event.thumbnail = save_image(image_file=thumbnail, destination='thumbnail', method='replace', prev_filename=event.thumbnail, max_size=(480, 270))

        if proof_data:
            header, data = proof_data.split(';base64,')
            proof = b64decode(data)  # This should be the binary image data
            event.proof = save_image(image_file=proof, destination='proof', method='replace', prev_filename=event.proof, max_size=(720, 405))

        try:
            points = int(points)
        except ValueError:
            flash("Points must be an integer.", category='error')

        if points < 1 or points > 4:
            flash("Points must be from 1 to 4.", category='error')

        # Update other fields
        event.name = name
        event.short_name = short_name.lower()
        event.date = datetime.strptime(date, "%Y-%m-%d").date()
        event.venue = venue
        event.points = points
        event.reflection = reflection
        event.category_id = category_id
        event.organizer_id = organizer_id

        db.session.commit()

        return redirect(url_for('admin.editable_events'))

    return render_template('event_form.html', event=event, categories=categories, organizers=organizers, user=current_user)

@admin.route('/admin/upload-summary', methods = ['GET', 'POST'])
@login_required
def upload_summary():
    if request.method == 'POST':
        summary = request.files['summary']
        previous_summary = current_user.summary  # Store the current summary for reference
        if summary:
            # Call save_pdf function, passing the previous summary
            new_summary_filename = save_pdf(summary, previous_summary)
            # If the summary was saved successfully, update the user summary
            if new_summary_filename:
                current_user.summary = new_summary_filename
                # Commit the change to the database
                db.session.commit()  # Assuming you are using SQLAlchemy
                return redirect(url_for('admin.admin_home'))
    return render_template('summary_form.html', user=current_user)

@admin.route('/delete-organizer/<organizer_id>', methods=['POST'])
@login_required
def delete_organizer(organizer_id):
    organizer = models.Organizer.query.filter_by(id=organizer_id, user_id=current_user.id).first()
    events_count = models.Event.query.filter_by(organizer_id=organizer_id, user_id=current_user.id).count()

    if events_count > 0:
        flash(f"Cannot delete organizer with ID {organizer_id}, it has {events_count} associated events.", category='error')
        return redirect(url_for('admin.editable_organizers'))

    if not organizer:
        abort(404, description="Organizer not found.")

    if organizer.logo:
        delete_image(filename=organizer.logo, folder='organizer')

    db.session.delete(organizer)
    db.session.commit()

    return redirect(url_for('admin.editable_organizers'))

@admin.route('/delete-event/<event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = models.Event.query.filter_by(id=event_id, user_id=current_user.id).first()

    if not event:
        abort(404, description="Event not found.")

    if event.thumbnail:
        delete_image(filename=event.thumbnail, folder='thumbnail')

    if event.proof:
        delete_image(filename=event.proof, folder='proof')

    db.session.delete(event)
    db.session.commit()

    return redirect(url_for('admin.editable_events'))

@admin.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', description=e.description, user=current_user), 404
