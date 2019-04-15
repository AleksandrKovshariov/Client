import re
import json
import requests
import datetime
import mimetypes

from flask import Blueprint, render_template, request, session
from flask import Response

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


@bp.route('/delete/<path:sub_path>')
@login_required
def delete(sub_path):
    access_token = session['access_token']
    file = '/resource/' + sub_path
    try:
        req = requests.delete(RES_PATH + file, headers={
            'Authorization': 'Bearer {}'.format(access_token)})
        if not req.status_code == 200:
            return render_error(req)
        return render_template('files/file_deleted.html')
    except requests.exceptions.RequestException:
        return render_template('service_not_available.html', message="Can't send a request to the server")


@bp.route('/access')
@login_required
def access():
    access_token = session['access_token']
    try:
        req = requests.get(RES_PATH + request.script_root + request.full_path, headers={
            'Authorization': 'Bearer {}'.format(access_token)})
    except requests.exceptions.RequestException:
        return render_template('service_not_available.html', message="Can't send a request to the server")

    if not req.status_code == 200:
        return render_error(req)

    accesses = json.loads(req.text).get('access')
    for acc in accesses:
        acc['accessType'] = re.sub("[\][]", "", acc['accessType'])
        path = acc['path']
        acc['pathToRoot'] = path[0:path.rfind('/') + 1]

    return render_template('files/accesses.html', accesses=accesses)


def parse_dir_structure(text):
    contents = json.loads(text)
    files = contents.get('files')

    array = []
    for f in files or []:
        file = json.loads(f)
        file['modified'] = datetime.datetime.fromtimestamp(file['modified'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        extension = file['name'][str.rfind(file['name'], '.'):]
        try:
            mime = mimetypes.types_map[extension]
            file['MimeType'] = mime[0 : str.rfind(mime, '/')]
        except KeyError:
            file['MimeType'] = None
            file['metric'] = ' '
        if not file['size'] == ' ':
            kb = int(file['size']) / 1024
            if kb > 1024:
                file['size'] = int(round(kb / 1024, 0))
                file['metric'] = "MB"
            else:
                file['size'] = round(kb, 1)
                file['metric'] = "KB"

        array.append(file)
    return array


@bp.route('/resource/<path:sub_path>')
@login_required
def resource(sub_path):
    access_token = session['access_token']
    try:
        req = requests.get(RES_PATH + request.full_path, headers={
            'Authorization': 'Bearer {}'.format(access_token)
        }, stream=True)

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
    return Response(req.iter_content(chunk_size=1024), headers=req.headers.items())

@bp.route('/manage', methods=('GET', 'POST'))
@login_required
def manage():
    access_token = session['access_token']

    try:
        r = requests.get(RES_PATH + '/access?access_type=GRANT', headers={
            'Authorization': 'Bearer {}'.format(access_token)})
        if not r.status_code == 200:
            return render_error(r)
    except requests.exceptions.RequestException:
        return render_template('service_not_available.html', message='Cant send request to authorization server')

    accesses = json.loads(r.text).get('access')

    if request.method == 'POST':
        access_list = request.form.getlist('access')
        accesses = 'READ,'

        for a in access_list:
            accesses += a + ','
        json_req = {
            'to_user': request.form['username'],
            'path': request.form['path'],
            'access_type': accesses[:-1]
        }
        print(json_req)

        try:
            r = requests.post(RES_PATH + '/access', headers={
            'Authorization': 'Bearer {}'.format(access_token)}, json=json_req)
            if not r.status_code == 200:
                return render_error(r)
        except requests.exceptions.RequestException:
            return render_template('service_not_available.html', message='Cant send request to authorization server')

        access = json.loads(r.text)
        print(access)
        return render_template('files/adding_access_success.html', accesses=access)


    return render_template('files/manage.html', accesses=accesses)


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
        try:
            r = requests.post(RES_PATH + '/resource', headers={
                'Authorization': 'Bearer {}'.format(access_token),
                'Content-Length': request.headers.get('Content-Length'),
                'Content-Type': request.headers.get('Content-Type')}, data=request.stream)

            if not r.status_code == 200:
                return render_error(r)

        except requests.exceptions.RequestException:
            return render_template('service_not_available.html', message="Can't send a request to the server")

        path = json.loads(r.text).get('saved')
        return render_template('files/upload_seccess.html', path=path)

    return render_template('files/upload.html', access_dir=access_dir)
