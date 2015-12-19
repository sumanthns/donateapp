#!/bin/bash

gunicorn --workers=1 --threads=5 --log-level=debug app:app
