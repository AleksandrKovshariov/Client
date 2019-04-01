import json
import requests
import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from auth_settings import AUTH_PATH, CLIENT_ID, CLIENT_SECRET
from files import render_error


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            req = requests.post(AUTH_PATH, data={
                'grant_type': 'password',
                'username': username,
                'password': password,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
            })
        except requests.exceptions.RequestException:
            return render_template('service_not_available.html', message="Can't send a request to the server")

        if req.status_code != 200:
            return render_error(req)

        contents = json.loads(req.text)

        session.clear()
        session['access_token'] = contents.get('access_token')
        session['username'] = username
        return redirect(url_for('files.access'))

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@bp.before_app_request
def load_logged_in_user():
    g.access_token = session.get('access_token')
    g.username = session.get('username')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.access_token is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
