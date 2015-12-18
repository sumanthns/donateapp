from app.models import User
from flask_wtf import Form
from flask_wtf.recaptcha import validators
from wtforms import StringField, PasswordField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Regexp


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(
            email=self.email.data).first()
        if user is None:
            self.email.errors.append('Invalid email or password')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid email or password')
            return False

        self.user = user
        return True


class RegisterForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Name', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    confirm_password = StringField('Confirm Password', validators=[DataRequired()])
    seed = HiddenField("seed")

    def __init__(self, user, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = user

    def validate(self):
        if not Form.validate(self):
            return False

        if self.user is None:
            user = User.query.filter_by(
                email=self.email.data).first()
            if user is not None:
                self.email.errors.append("Email already taken")
                return False

        if not self.password.data == self.confirm_password.data:
            self.password.errors.append("Passwords dont match")
            return False

        return True


class ForgotPasswordForm(Form):
    email = StringField('Email', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    confirm_password = StringField('Confirm Password', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        if not Form.validate(self):
            return False

        self.user = User.query.filter_by(
            email=self.email.data).first()
        if self.user is None:
            self.email.errors.append("User doesnt not exist")
            return False

        if not self.password.data == self.confirm_password.data:
            self.password.errors.append("Passwords dont match")
            return False

        return True

class RequestDonationForm(Form):
    email1 = StringField('Email1', validators=[DataRequired()])
    email2 = StringField('Email2', validators=[DataRequired()])
    payment_request_id = HiddenField('payment_request_id')

class DonateForm(Form):
    amount = StringField('Amount', validators=[DataRequired(), Regexp(r'^[0-9]+$')])

    def validate(self):
        if not Form.validate(self):
            return False
        amount = int(self.amount.data)
        if amount < 9 or amount > 200000:
            self.amount.errors.append("Min is 9 and Max in 200000")
            return False
        return True
