def test_app(app):
    app.get('/', status=404)
