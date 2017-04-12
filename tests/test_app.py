def test_404(app):
    app.get('/', status=404)


def test_response_as_str(app):
    resp = app.get('/index', status=200)
    assert resp.content_type == 'text/plain'
    assert resp.text == 'this is index'
