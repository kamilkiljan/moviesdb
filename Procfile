release: python moviesdb/manage.py makemigrations api --no-input
release: python moviesdb/manage.py migrate --run-syncdb --no-input
web: python moviesdb/manage.py runserver 0.0.0.0:$PORT