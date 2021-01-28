from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bubbles.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Bubble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(250), nullable=False)
    when = db.Column(db.String(50), nullable=False)
    is_complete = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {column.description: getattr(self, column.description) for column in self.__table__.columns}


db.create_all()


class BubbleForm(FlaskForm):
    bubble_description = StringField('', validators=[DataRequired()], render_kw={"autofocus": True,
                                                                                 "autocomplete": 'off',
                                                                                 "placeholder": "Bubble description"})
    when_due = SelectField('', choices=["Due today", "Due this week", "Due later(ish)"])
    submit = SubmitField('Submit')


def convert_to_bool(answer):
    if answer == "Yes":
        return True
    else:
        return False


@app.route("/", methods=["GET", "POST"])
def home():
    form = BubbleForm()
    if form.validate_on_submit():
        new_bubble = Bubble(
            description=form.bubble_description.data,
            when=form.when_due.data,
            is_complete=False
        )
        db.session.add(new_bubble)
        db.session.commit()
        return redirect(url_for("home"))
    all_active_bubbles = Bubble.query.all()
    bubbles_today = [bubble for bubble in all_active_bubbles if bubble.when == "Due today" and not bubble.is_complete]
    bubbles_this_week = [bubble for bubble in all_active_bubbles if bubble.when == "Due this week" and not bubble.is_complete]
    bubbles_later = [bubble for bubble in all_active_bubbles if bubble.when == "Due later(ish)" and not bubble.is_complete]
    return render_template("index.html", bubbles_today=bubbles_today, bubbles_this_week=bubbles_this_week, bubbles_later=bubbles_later, form=form)


@app.route("/popped", methods=["GET", "POST"])
def popped():
    form = BubbleForm()
    if form.validate_on_submit():
        new_bubble = Bubble(
            description=form.bubble_description.data,
            when=form.when_due.data,
            is_complete=False
        )
        db.session.add(new_bubble)
        db.session.commit()
        return redirect(url_for("home"))
    all_bubbles = Bubble.query.all()
    popped_bubbles = [bubble for bubble in all_bubbles if bubble.is_complete]
    return render_template("popped.html", popped_bubbles=popped_bubbles, form=form)


@app.route("/pop")
def pop():
    bubble_id = request.args.get("id")
    bubble_to_update = Bubble.query.get(bubble_id)
    bubble_to_update.is_complete = True
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
