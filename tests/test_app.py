import utils

from webtest import Upload


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
