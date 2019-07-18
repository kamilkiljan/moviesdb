## moviesdb - Django REST API example

**moviesdb** is a simple REST API built using Django web framework.

### Installation
1. Clone the repository to a directory on your computer: 

    `git clone https://github.com/kamilkiljan/moviesdb.git`
    
2. Create virtual environment:

    `python3 -m venv venv`
    
3. Activate virtual environment:

    `source venv/bin/activate`
    
4. Install required python packages:

    `pip install -r requirements.txt`
    
5. Change the directory to moviesdb and prepare and run model-database migrations:
    
    `cd moviesdb`
    
    `python manage.py makemigrations api`
    
    `python manage.py migrate`
    
6. Run server on 0.0.0.0:8000:

    `python manage.py runserver 0.0.0.0:8000`
    
---
**Alternatively**, you can dockerize the application in the following way:

1. Clone the repository to a directory on your computer: 

    `git clone https://github.com/kamilkiljan/moviesdb.git`

2. Build the docker image:

    `docker build . --tag=moviesdb:0.1`

3. Run the container using the created image:
    
    `docker-compose up --abort-on-container-exit`

---
### API endpoints

The API has the following endpoints:

1. **api/movies/**

    - **GET** request lists all movies and related ratings present in the database
    - **POST** request creates movie record and related rating records in the database 
        - *title* field is the title of the movie to be fetched from OMDB
    
2. **api/comments/**

    - **GET** request lists all comments present in the database
        - *movie_id* parameter (optional) narrows query to comments for movie with provided ID
    - **POST** request creates comment for selected movie
        - *movie_id* field is the ID of commented movie
        - *comment_body* field is the text of the comment
        
3. **api/top/**

    - **GET** request lists movies ranked by the number of comments added within specified date range
        - *date_start* and *date_end* parameters specify the date range (both are inclusive)
        
---
### Secret keys (moviesdb/moviesdb/secret_keys.py)

**Always remember to change the secret keys in production**. Also, you can request an OMDB API key here: http://www.omdbapi.com/apikey.aspx 