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


def test_url_argument_parsing(app):
    resp = app.get('/users/120u12a/', status=200)
    assert resp.text == '120u12a'


def test_url_qs_parsing(app):
    resp = app.get('/index/?user=Cartman&from=Southpark')
    assert resp.text == 'Hello Cartman from Southpark !'
