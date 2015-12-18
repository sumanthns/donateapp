from app import db
from app.admin.views.auth_mixin import admin_login_required
from app.models import User, Payment
from config import ADMIN_USERS_PER_PAGE
from flask import render_template
from flask_admin import BaseView, expose
from sqlalchemy import func


class MyAdmin(BaseView):
    @expose('/')
    @expose('/<int:page>')
    @admin_login_required
    def index(self, page=1):
        total_donation = db.session.query(
            func.sum(Payment.amount).label('sum')) \
            .filter(Payment.status == 'Credit').first()[0]

        user_payments = {}
        users = User.query.filter_by(role=None).paginate(
            page, ADMIN_USERS_PER_PAGE, False)
        if users:
            for user in users.items:
                user_payments[user.name] = sum(payment.amount
                                               for payment in user.payments
                                               if payment.amount is not None
                                               and payment.status == 'Credit')

        return render_template('admin/index.html',
                               user_payments=user_payments,
                               total_donation=total_donation,
                               users=users)