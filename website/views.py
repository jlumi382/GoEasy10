from flask import render_template, abort, Blueprint, request
from flask_login import current_user
from . import models

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("index.html", user=current_user)

@views.route('/<user_id>')
def viewer_home(user_id):
    user = models.User.query.get(int(user_id))

    if not user:
        abort(404, description="Journal owner not found.")


    return render_template("viewer_home.html", user=current_user, user_id=user.id)

@views.route('/<user_id>/summary')
def summary(user_id):
    user = models.User.query.get(int(user_id))
    return render_template("summary.html", user=user)

@views.route('/<user_id>/<category>')
def category_page(user_id, category):
    user = models.User.query.get(int(user_id))
    category = models.Category.query.filter_by(short_name=category).first()

    if not user:
        abort(404, description="Journal owner not found.")

    if not category:
        abort(404, description="Category not found.")

    path = f'/{user.id}/{category.short_name}'

    events = models.Event.query.filter_by(category_id=category.id, user_id=user.id)
    total_points = sum(event.points for event in events)

    return render_template("category.html", category=category, events=events, user=current_user, user_id=user.id, total_points=total_points, path=path)

@views.route('/<user_id>/<category>/<event_id>')
def event_page(user_id, category, event_id):
    category = models.Category.query.filter_by(short_name=category).first()

    if not category:
        abort(404, description="Category not found.")

    event = models.Event.query.filter_by(id=event_id, category_id=category.id, user_id=user_id).first()

    if not event:
        abort(404, description="Event not found.")

    organizer = event.organizer

    if not organizer:
        abort(404, description="Organizer not found.")

    return render_template("reflection.html", category=category, event=event, organizer=organizer, user=current_user, user_id=user_id)

@views.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', description=e.description, user=current_user), 404
