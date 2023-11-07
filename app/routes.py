# -*- coding: utf-8 -*-
from flask import render_template, request,redirect, url_for, send_file, flash, abort, Response


from app import app
from app.errors import page_not_found

import pytz

from datetime import datetime, timedelta

from io import BytesIO


@app.route('/', methods = ['POST', 'GET'])
@app.route('/index', methods = ['POST', 'GET'])
def index():
    return render_template('index.html')


@app.route('/404/<err>')
def not_found_error(err='No page found'):
    if err == 'file':
        err = '404  No files found'
    return render_template('404.html',error=err), 404