import os
import json
import requests
import datetime

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    from auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from files import bp as files_bp
    app.register_blueprint(files_bp)
    app.add_url_rule('/', endpoint='index')

    return app

    # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    # context.load_cert_chain('domain.crt', 'domain.key')
    # app.run(port = 5000, debug = True, ssl_context = context)

if __name__ == '__main__':
    create_app().run();

# @app.before_request
# def before_request():
#     if request.endpoint not in ['login', 'request_token']:
#         access_token = request.cookies.get('access_token')
#         if access_token:
#             pass
#         else:
#             return redirect(url_for('login'))
#
#
# def parse_dir_structure(text):
#     contents = json.loads(text)
#     users = contents.get('files')
#
#     array = []
#     for user in users:
#         file = json.loads(user)
#         file['modified'] = datetime.datetime.fromtimestamp(file['modified'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
#         array.append(file)
#     return array
#
#
# @app.route('/access')
# def access():
#     access_token = request.cookies.get('access_token')
#     r = requests.get(RES_PATH + '/access', headers={
#         'Authorization': 'Bearer {}'.format(access_token)})
#     print(r.status_code)
#     content = json.loads(r.text).get('access')
#     return render_template('accesses.html', accesses=content)
#
#
# @app.route('/resource/<path:subpath>')
# def resourse(subpath):
#     access_token = request.cookies.get('access_token')
#     r = requests.get(RES_PATH + '/resource/' + subpath, headers={
#         'Authorization': 'Bearer {}'.format(access_token)
#     })
#
#     if r.status_code != 200:
#         return json.dumps({
#             'error': 'The resource server returns an error: \n{}'.format(
#                 r.text)
#         }), 500
#
#     if r.headers.get('Type') == 'directory':
#         return render_template('files.html', users=parse_dir_structure(r.text))
#
#     return r.content, r.status_code, r.headers.items()
#
#
# @app.route('/login')
# def login():
#     # Presents the login page
#     return render_template('login.html')
#
#
# @app.route('/request_token', methods=['POST'])
# def request_token():
#     # Requests access token from the authorization server
#     username = request.form.get('username')
#     password = request.form.get('password')
#     r = requests.post(AUTH_PATH, data={
#         'grant_type': 'password',
#         'username': username,
#         'password': password,
#         'client_id': CLIENT_ID,
#         'client_secret': CLIENT_SECRET,
#     })
#
#     if r.status_code != 200:
#         return json.dumps({
#             'error': 'The authorization server returns an error: \n{}'.format(
#                 r.text)
#         }), 500
#
#     contents = json.loads(r.text)
#     access_token = contents.get('access_token')
#
#     response = make_response(redirect(request.url_root + 'resource/' + username + '/'))
#     response.set_cookie('access_token', access_token)
#
#     return response
