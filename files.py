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
    req = requests.get(RES_PATH + '/resource/' + sub_path, headers={
        'Authorization': 'Bearer {}'.format(access_token)
    })

    if req.status_code != 200:
        return render_template('service_not_available.html')

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

    if request.method == 'POST':
        if 'file' not in request.files or request.files['file'].filename == '':
            return render_template('files/upload.html', file_not_found=True)
        file = request.files['file']
        to_dir = request.form['to_dir']

        # TODO
        # Реквест на сохранением файла,
        # если успех запиши в переменную path путь к новому файлу
        path = "path/to/file/file.type"

        return render_template('files/upload.html', path=path)

    r = requests.get(RES_PATH + '/access', headers={
        'Authorization': 'Bearer {}'.format(access_token)})
    access_dir = json.loads(r.text).get('access')

    return render_template('files/upload.html', access_dir=access_dir)
