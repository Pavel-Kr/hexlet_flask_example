start:
	poetry run flask --app hexlet_flask_example.example --debug run --port 8000

install:
	poetry install

run:
	poetry run gunicorn --workers=4 --bind=127.0.0.1:8000 hexlet_flask_example.example:app
