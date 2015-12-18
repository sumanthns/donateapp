import urllib
import uuid
import datetime

from app import lm, app, db, payment_gateway_api
from app.forms import LoginForm, RegisterForm, ForgotPasswordForm, RequestDonationForm, DonateForm
from app.helpers import send_email, verify_mac, send_thankyou_email
from app.models import User, Payment
from config import ADMINS, HOSTNAME, DATABASE_QUERY_TIMEOUT
from flask import request, url_for, render_template, g, flash
from flask_login import login_user, logout_user, current_user, login_required
from flask_sqlalchemy import get_debug_queries
from werkzeug.utils import redirect


@app.route("/")
@app.route('/index')
def index():
    return render_template('index.html')


@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(request.args.get('next') or url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        flash("Logged in successfully")
        login_user(form.user, remember=form.remember_me.data)
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.before_request
def before_request():
    g.user = current_user


@app.route('/forgot_password', methods=["GET", "POST"])
def forgot_password():
    if g.user is not None and g.user.is_authenticated:
        flash("Already logged in", "error")
        return redirect(request.args.get('next') or url_for('index'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = form.user
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash("Password changed successfully")
        return redirect(request.args.get('next') or url_for('login'))

    return render_template('forgot_password.html', form=form)


@app.route('/register', methods=["GET", "POST"])
def register():
    user = None
    if g.user is not None and g.user.is_authenticated:
        flash("Already registered")
        return redirect(request.args.get('next') or url_for('index'))

    if request.method == 'GET':
        seed = request.args.get('seed', None)
        form = RegisterForm(user=user, seed=seed)
    else:
        form = RegisterForm(user=user)

    if form.validate_on_submit():
        user = User(name=form.name.data,
                    email=form.email.data,
                    password=form.password.data,
                    uuid=str(uuid.uuid4()))
        if form.seed.data is not None:
            parent_user = User.query.filter_by(uuid=form.seed.data).first()
            if parent_user:
                user.parent_id = parent_user.id
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/request_donate", methods=["GET", "POST"])
@login_required
def request_donate():
    form = RequestDonationForm()
    if request.args.get('payment_request_id'):
        form.payment_request_id = request.args.get('payment_request_id')

    if form.validate_on_submit():
        seed = g.user
        subject = "%s requests you to donate for the cause!" \
                  % seed.name
        sender = ADMINS[0]
        link = "{0}/register?seed={1}".format(HOSTNAME, seed.uuid)
        text_body = render_template('donate_request.txt',
                                    seed=seed.name, link=link)
        html_body = render_template('donate_request.html',
                                    seed=seed.name, link=link)
        recipients = [form.email1.data, form.email2.data]
        send_email(subject, sender, recipients,
                   text_body, html_body)
        flash("Sent request to donors. Thank you for your support!")
        return redirect(url_for('index'))
    return render_template('request_donate.html', form=form, user_id=g.user.id)


@app.route("/donate", methods=["GET", "POST"])
@login_required
def donate():
    form = DonateForm()
    if form.validate_on_submit():
        redirect_url = "{0}/request_donate".format(HOSTNAME)
        amount = form.amount.data
        purpose = "donateapp"
        email = g.user.email
        webhook = "{0}/payment_gateway_webhook".format(HOSTNAME)
        allow_repeated_payments = False

        response = payment_gateway_api.payment_request_create(
            purpose=purpose,
            amount=amount,
            redirect_url=redirect_url,
            email=email,
            webhook=webhook,
            allow_repeated_payments=allow_repeated_payments
        )

        payment = Payment(user_id=g.user.get_id(),
                          payment_request_id=response['payment_request']['id'],
                          payment_url=response['payment_request']['longurl'],
                          amount=amount,
                          status='pending')
        db.session.add(payment)
        db.session.commit()
        return redirect(response['payment_request']['longurl'])
    flash("Thank you for your support!")
    return render_template('donate.html', form=form)


@app.route("/users/<user_id>/payments/<payment_request_id>",
           methods=["GET"])
def get_payment(user_id, payment_request_id):
    if g.user and g.user.is_authenticated:
        if g.user.get_id() == user_id:
            payment = g.user.payments.filter_by(
                payment_request_id=payment_request_id).first()
            if payment:
                return payment.status, 200
    return None


@app.route("/payment_gateway_webhook", methods=["POST"])
def payment_ack():
    #Set content-type to application/json
    if request.environ['CONTENT_TYPE'] == 'application/x-www-form-urlencoded':
        request.environ['CONTENT_TYPE'] = 'application/json'
    urldecoded_data = urllib.unquote(request.data).\
        decode('utf8')
    url_components = urldecoded_data.split('&')
    if not url_components:
        return "No data sent", 400

    url_dict = {}
    for comp in url_components:
        k, v = comp.split('=')
        url_dict[k] = v

    print url_dict
    if not verify_mac(url_dict):
        return "Mac not authenticated", 401

    payment = Payment.query.filter_by(
        payment_request_id=url_dict['payment_request_id']
    ).first()

    if not payment:
        # payment was requested made by system, not sure what to do
        return
    payment.payment_id = url_dict['payment_id']
    payment.status = url_dict['status']
    payment.donated_on = datetime.datetime.utcnow()
    db.session.add(payment)
    db.session.commit()
    user = payment.user
    send_thankyou_email(user=user, amount=payment.amount)
    return "Success!", 200


@app.route("/my_donations", methods=["GET"])
@login_required
def my_donations():
    donations = g.user.payments.all()
    return render_template("my_donations.html", donations=donations)


@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= DATABASE_QUERY_TIMEOUT:
            app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (
                query.statement, query.parameters, query.duration, query.context))
    return response

