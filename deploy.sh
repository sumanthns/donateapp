#!/bin/bash

echo Pushing code to heroku
git push heroku master

echo Stopping dynos
heroku ps:scale web=0
heroku ps:scale upgrade=0

echo Upgrading database
heroku ps:scale upgrade=1
heroku ps:scale upgrade=0

echo Starting dynos
heroku ps:scale web=1

echo Done

