from app import db
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash,\
    check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), index=True, unique=True)
    _password = db.Column(db.String(124))
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    children = db.relationship("User")
    uuid = db.Column(db.String(124))
    payments = db.relationship('Payment', backref='user', lazy='dynamic')
    role = db.Column(db.String(64))

    def __repr__(self):
        return '<User %r>' % (self.name)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def set_password(self, plaintext):
        self._password = generate_password_hash(plaintext)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_admin(self):
        return self.is_authenticated and self.has_role('Admin')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def has_role(self, role):
        return self.role == role


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    payment_request_id = db.Column(db.String(124))
    payment_id = db.Column(db.String(124))
    status = db.Column(db.String(64))
    amount = db.Column(db.Integer)
    payment_url = db.Column(db.String(124))
    donated_on = db.Column(db.DateTime)

    def __repr__(self):
        return '<Payment %r>' % (self.id)
