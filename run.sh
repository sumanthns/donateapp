#!/bin/bash
export DATABASE_URL="mysql://root@localhost/donateapp"
export PAYMENT_GW_API_KEY='e73d335de204715e2b05446d0191e3dc'
export PAYMENT_GW_AUTH_TOKEN='1ff3c01b1f8862fc7a3bf0594594591b'
export PAYMENT_GW_SALT='de113111b6ff4f1ea43613623a742d66'
gunicorn --workers=1 --threads=5 --log-level=debug app:app
