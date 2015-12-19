web: gunicorn --log-level=info --threads=5 --workers=1 app:app
init: python db_create.py
upgrade: python db_upgrade.py