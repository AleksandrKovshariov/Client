import json
import requests
import datetime

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, session
from werkzeug.exceptions import abort

from auth import login_required

from resource_settings import RES_PATH


bp = Blueprint('files', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/access')
@login_required
def access():
    access_token = session['access_token']
    r = requests.get(RES_PATH + '/access', headers={
        'Authorization': 'Bearer {}'.format(access_token)})
    content = json.loads(r.text).get('access')
    return render_template('files/accesses.html', accesses=content)


def parse_dir_structure(text):
    contents = json.loads(text)
    users = contents.get('files')

    array = []
    for user in users:
        file = json.loads(user)
        file['modified'] = datetime.datetime.fromtimestamp(file['modified'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        array.append(file)
    return array


@bp.route('/resource/<path:sub_path>')
@login_required
def resource(sub_path):
    access_token = session['access_token']
    req = requests.get(RES_PATH + sub_path, headers={
        'Authorization': 'Bearer {}'.format(access_token)
    })

    if req.status_code != 200:
        return json.dumps({
            'error': 'The resource server returns an error: {}'.format(
                req.text)
        }), 500

    if req.headers.get('Type') == 'directory':
        return render_template('files/files.html', files=parse_dir_structure(req.text))

    return req.content, req.status_code, req.headers.items()
