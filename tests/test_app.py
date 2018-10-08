import wsgiref

from spewe import http
from spewe import Settings, Spewe

import utils

from webtest import Upload


def test_request():
    env = {
        "CONTENT_LENGTH": "",
        "CONTENT_TYPE": "text/plain",
        "HTTP_ACCEPT": "*/*",
        "HTTP_ACCEPT_ENCODING": "gzip, deflate",
        "HTTP_CONNECTION": "keep-alive",
        "HTTP_HOST": "localhost:8099",
        "HTTP_USER_AGENT": "HTTPie/0.9.3",
        "PATH_INFO": "/users",
        "QUERY_STRING": "username=toto&email=toto@toto.org",
        "REMOTE_ADDR": "127.0.0.1",
        "REMOTE_HOST": "localhost",
        "REQUEST_METHOD": "GET",
        "SCRIPT_NAME": "",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "8099",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "SERVER_SOFTWARE": "WSGIServer/0.1 Python/2.7.13",
        "_": "/usr/bin/python",
        "wsgi.version": "(1, 0)",
        "wsgi.run_once": False,
        "wsgi.multiprocess": False,
        "wsgi.url_scheme": "http",
        "wsgi.multithread": True,
    }
    wsgiref.util.setup_testing_defaults(env)
    request = http.Request(env)
    assert request.scheme == 'http'
    assert request.method == 'GET'
    assert request.path == '/users'
    assert request.query_string == "username=toto&email=toto@toto.org"
    assert request.content_type == "text/plain"
    assert request.content_length == ""
    assert request.server_port == "8099"
    assert request.server_name == "localhost"
    assert request.remote_address == "127.0.0.1"
    assert request.get_full_path() == "http://localhost:8099/users"
    uuid = 'abcd' * 8
    assert request.build_absolute_uri(uuid) == "http://localhost:8099/%s" % uuid


def test_none_response(app):
    app.get('/none/', status=204)


def test_404(app):
    app.get('/', status=404)


def test_405_method_not_allowed(app):
    app.post('/index', status=405)


def test_response_default_headers(app):
    resp = app.get('/index', status=200)
    assert resp.headers['Content-Type'] == 'text/html; charset=UTF8'
    assert resp.headers['Content-Length'] == '27'
    assert resp.headers['Server'] == 'localhost'
    assert 'Date' in resp.headers


def test_response_as_str(app):
    resp = app.get('/index', status=200)
    assert resp.content_type == 'text/html'
    assert resp.text == 'Hello world from universe !'


def test_form_submission(app):
    # failed authentication
    payload = {'username': 'loking', 'password': 'lokinghdx'}
    resp = app.post('/login', params=payload, status=200)
    assert resp.html.find('div', {'class': 'error'}).text.strip() == u"Invalid credentials"
    # successful authentication
    resp.form['username'] = 'loking'
    resp.form['password'] = 'lokinghd'
    resp = resp.form.submit()
    assert resp.html.find('div', {'authenticated'}).p.text.strip() == 'Hello Loking !'


def test_form_submission_with_file(app):
    uuid = 'abcd' * 8
    url = '/users/%s/notes/' % uuid
    filename = 'issue25.txt'
    filecontent = 'CBV in da place baby !!!'.encode('utf-8')
    resp = app.get(url)
    resp.form['description'] = 'little note about the issue #25'
    resp.form['note'] = Upload(filename, filecontent, 'text/plain')
    resp = resp.form.submit()
    assert resp.html.find('span', {'class': 'note-title'}).text.strip() == filename
    assert resp.html.find('p', {'class': 'note-content'}).text.strip() == filecontent.decode()


def test_url_argument_parsing(app):
    resp = app.get('/users/120u12a/', status=200)
    assert resp.text == '120u12a'


def test_url_qs_parsing(app):
    resp = app.get('/index/?user=Cartman&from=Southpark')
    assert resp.text == 'Hello Cartman from Southpark !'


def test_app_absent_template(app):
    resp = app.get('/notemplate/', status=404)
    tpl_filepath = utils.get_test_app_template('none.html')
    assert 'template %s not found' % tpl_filepath in resp.text


def test_json_payload(app):
    url = '/api/users/'
    resp = app.get(url)
    assert len(resp.json) == 1
    assert resp.json[0]['username'] == 'cloking'
    payload = {'username': 'jloking', 'email': 'jloking@lk.corp'}
    resp = app.post_json('/api/users/', params=payload)
    assert len(resp.json) == 2
    assert resp.json[1]['username'] == 'jloking'
    assert resp.json[1]['uuid'] == 'aabb' * 8


def test_response_redirect(app):
    url = 'https://example.net/'
    response = http.ResponsePermanentRedirect(url)
    assert response.headers['Location'] == url
    assert response.status_code == 301
    response = http.ResponseRedirect(url)
    assert response.headers['Location'] == url
    assert response.status_code == 302


def test_app_settings():
    app = Spewe()
    assert app.settings.DEBUG is False
    assert app.settings['DEBUG'] is False
    csettings = Settings(
        DEBUG=True,
        TEMPLATE_DIR='templates',
        STATIC_DIR='statics',
    )
    app = Spewe(settings=csettings)
    assert app.settings.DEBUG is True
    assert app.settings.TEMPLATE_DIR == 'templates'
    assert app.settings.STATIC_DIR == 'statics'
