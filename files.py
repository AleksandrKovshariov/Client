import re
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


def render_error(req):
    try:
        error_type = json.loads(req.text).get('error')
        print(error_type)
        if error_type is None:
            return render_template('service_not_available.html', message="This is strange...")
        return render_template('service_not_available.html', message=error_type)
    except ValueError:
        return render_template('service_not_available.html', message='Whooops... resource server error')


@bp.route('/access')
@login_required
def access():
    access_token = session['access_token']
    try:
        req = requests.get(RES_PATH + request.script_root + request.full_path, headers={
            'Authorization': 'Bearer {}'.format(access_token)})
    except requests.exceptions.RequestException:
        return render_template('service_not_available.html', message="Can't send a request to the server")

    print(req.status_code)
    if not req.status_code == 200:
        return render_error(req)

    accesses = json.loads(req.text).get('access')
    for acc in accesses:
        acc['accessType'] = re.sub("[\][]", "", acc['accessType'])

    return render_template('files/accesses.html', accesses=accesses)


def parse_dir_structure(text):
    contents = json.loads(text)
    files = contents.get('files')

    array = []
    for f in files:
        file = json.loads(f)
        file['modified'] = datetime.datetime.fromtimestamp(file['modified'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        array.append(file)
    return array


@bp.route('/resource/<path:sub_path>')
@login_required
def resource(sub_path):
    access_token = session['access_token']
    try:
        req = requests.get(RES_PATH + '/resource/' + sub_path, headers={
            'Authorization': 'Bearer {}'.format(access_token)
        })
    except requests.exceptions.RequestException:
        return render_template('service_not_available.html', message="Can't send a request to the server")

    if req.status_code != 200:
        return render_error(req)

    if req.headers.get('Type') == 'directory':
        sub_path = sub_path.split('/')
        if '' in sub_path:
            sub_path.remove('')
        dir = sub_path[-1]
        sub_path = sub_path[:-1]
        path = []
        for i, d in enumerate(sub_path):
            path.append((d, '/'.join(sub_path[:i + 1])))

        return render_template('files/files.html',
                               files=parse_dir_structure(req.text),
                               dir=dir,
                               path=path
                               )

    return req.content, req.status_code, req.headers.items()


@bp.route('/upload', methods=('GET', 'POST'))
@login_required
def upload():
    access_token = session['access_token']

    try:
        r = requests.get(RES_PATH + '/access?is_dir=true&access_type=write', headers={
            'Authorization': 'Bearer {}'.format(access_token)})
        if not r.status_code == 200:
            return render_error(r)
    except requests.exceptions.RequestException:
        return render_template('service_not_available.html', message='Cant send request to authorization server')

    access_dir = json.loads(r.text).get('access')

    if request.method == 'POST':
        if 'file' not in request.files or request.files['file'].filename == '':
            return render_template('files/upload.html', file_not_found=True, access_dir=access_dir)

        file = request.files['file']
        to_dir = request.form['to_dir']
        path = re.sub('[^A-Za-z0-9/\.]+', '',  to_dir + file.filename)
        try:
            r = requests.post(RES_PATH + '/resource/' + path, headers={
                'Authorization': 'Bearer {}'.format(access_token),
                'Content-Length': request.headers.get('Content-Length')}, data=file)

            if not r.status_code == 200:
                return render_error(r)

        except requests.exceptions.RequestException:
            return render_template('service_not_available.html', message="Can't send a request to the server")

        return render_template('files/upload.html', path=path, access_dir=access_dir)

    return render_template('files/upload.html', access_dir=access_dir)
