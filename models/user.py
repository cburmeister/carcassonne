from datetime import datetime
from flask import render_template
from flask_mail import Message
from flask_sqlalchemy import SQLAlchemy
from mail import mail

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(80), unique=True)

    turns = db.relationship('Turn', backref='user', lazy='dynamic')

    def send_email(self, subject, template, *args, **kwargs):
        """Sends the user an email."""
        msg = Message(
            subject,
            sender='noreply@carcassonne.io',
            recipients=[self.email]
        )
        msg.html = render_template(template, *args, **kwargs)
        mail.send(msg)
