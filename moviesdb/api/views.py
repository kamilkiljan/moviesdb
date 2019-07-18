import json
from datetime import datetime, timedelta
from urllib.error import URLError
from urllib.parse import quote_plus
from urllib.request import urlopen

from django.core.serializers import serialize
from django.db.models import Count, Q
from django.http.response import JsonResponse
from django.utils import timezone
from moviesdb.secret_keys import OMDB_API_KEY

from .models import Movie, Rating, Comment


def movies(request):
    """Movies API endpoint - listing and creating movie records"""

    # Get list of all movies in the database
    if request.method == 'GET':
        query = Movie.objects.all()
        response = {'content': [serialize_movie(m) for m in query],
                    'status': 200}
        return JsonResponse(response['content'], safe=False, status=response['status'])

    # Create new movie record in the database
    # based on the provided title with data fetched from OMDB.
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            url = 'http://www.omdbapi.com/?t={title}&r=json&apikey={api_key}'
            url = url.format(api_key=OMDB_API_KEY, title=quote_plus(title))
            try:
                omdb_response_dict = json.load(urlopen(url, timeout=10))
            except URLError:
                response = {'content': {'error': "Could not connect to OMDB API."},
                            'status': 400}
            else:
                if omdb_response_dict.get('Response') == "True":
                    try:
                        movie = Movie.objects.get(title=omdb_response_dict.get('Title'))
                    except Movie.DoesNotExist:
                        movie = None
                    if movie is None:
                        new_movie = Movie.create_from_omdb_dict(omdb_response_dict)
                        new_movie.save()

                        # Along with the movie record create related rating records
                        for rating_dict in omdb_response_dict.get('Ratings', []):
                            new_rating = Rating.create_from_rating_dict(new_movie, rating_dict)
                            new_rating.save()

                        response = {'content': serialize_movie(movie=new_movie),
                                    'status': 201}

                    else:
                        response = {'content': {'error': "The movie with this title is in the database."},
                                    'status': 409}
                else:
                    response = {'content': {'error': "The movie with this title was not found."},
                                'status': 404}
        else:
            response = {'content': {'error': "The title of the movie was not provided."},
                        'status': 400}
        return JsonResponse(response['content'], safe=False, status=response['status'])


def comments(request):
    """Comments API endpoint - listing and creating comments records"""

    # Get all comments in the database
    # (optionally filtered by movie_id parameter)
    if request.method == 'GET':
        movie_id = request.GET.get('movie_id')
        if movie_id is not None:
            query = Comment.objects.all().filter(movie=movie_id)
            if len(query) > 0:
                response = {'content': [serialize_comment(comment=c) for c in query],
                            'status': 200}
            else:
                response = {'content': {'error': "No comments for movie with this id were found."},
                            'status': 404}
        else:
            query = Comment.objects.all()
            if len(query) > 0:
                response = {'content': [serialize_comment(comment=c) for c in query],
                            'status': 200}
            else:
                response = {'content': [],
                            'status': 200}
        return JsonResponse(response['content'], safe=False, status=response['status'])

    # Create new comment record for selected movie_id
    # and with comment_body passed as request data
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        comment_body = request.POST.get('comment_body')
        if movie_id is not None and comment_body is not None:
            try:
                movie = Movie.objects.get(pk=movie_id)
                comment = Comment.objects.create(movie=movie, comment_body=comment_body)
                response = {'content': serialize_comment(comment),
                            'status': 201}
            except Movie.DoesNotExist:
                response = {'content': {'error': "The movie with this movie_id was not found."},
                            'status': 400}
        else:
            response = {'content': {'error': "The request should contain the movie_id and comment_body."},
                        'status': 400}
        return JsonResponse(response['content'], safe=False, status=response['status'])


def top(request):
    """
    Top API endpoint
    Getting movie IDs ranked by number of comments in specified date range
    """

    if request.method == 'GET':
        date_start = request.GET.get('date_start', '')
        date_end = request.GET.get('date_end', '')
        if date_start and date_end:
            try:
                date_start = from_iso(date_start)
                date_end = from_iso(date_end) + timedelta(days=1)
            except (ValueError, IndexError):
                response = {'content': {'error': "The date_start and date_end parameters "
                                                 "should be in ISO format "
                                                 "(yyyy-mm-dd, ie. 2019-12-31)."},
                            'status': 400}
            else:
                if date_start is not None and date_end is not None:

                    # Prepare aggregation only counting comments
                    # added within specified date range
                    com_count = Count('comment',
                                      filter=Q(comment__added__gte=date_start,
                                               comment__added__lt=date_end))
                    movies_qs = Movie.objects.annotate(com_count=com_count)

                    # Create list of dictionaries each containing
                    # movie ID and number of comments
                    movies_list = [{"movie_id": m.id, "total_comments": m.com_count} for m in movies_qs]
                    movies_list = sorted(movies_list, key=lambda d: d['total_comments'], reverse=True)

                    # Assign rank to each movie based on number of comments
                    # Movies with the most number of comments are rated highest
                    # Movies with the same number of comments have the same rank
                    min_count = None
                    current_rank = 0
                    for movie in movies_list:
                        if not current_rank:
                            min_count = movie['total_comments']
                            current_rank = 1
                        else:
                            if movie['total_comments'] < min_count:
                                current_rank += 1
                        movie['rank'] = current_rank
                    response = {'content': movies_list,
                                'status': 200}
        else:
            response = {'content': {'error': "The date_start and date_end parameters must be provided."},
                        'status': 400}
    return JsonResponse(response['content'], safe=False, status=response['status'])


def serialize_movie(movie):
    """
    Custom function to create json response payload
    consisting of movie details and related ratings
    """

    # Get query sets to be used with django serializer
    movie_query = Movie.objects.filter(pk=movie.pk)
    rating_query = Rating.objects.filter(movie=movie)

    # Movie dict consists of serialized movie's fields and movie_id
    movie_dict = json.loads(serialize('json', movie_query))[0]['fields']
    movie_dict.update({'movie_id': json.loads(serialize('json', movie_query))[0]['pk']})

    # Movie ratings is a list of related ratings
    ratings_list = [q['fields'] for q in json.loads(serialize('json', rating_query))]
    ratings_list = [{'source': r['source'], 'value': r['value']} for r in ratings_list]

    # Rating field does not appear if no ratings are related to the movie
    if ratings_list:
        movie_dict.update({'ratings': ratings_list})

    # Remove null values
    movie_dict = {k: v for (k, v) in movie_dict.items() if v is not None}
    return movie_dict


def serialize_comment(comment):
    """Custom function to create json response payload for a comment"""

    # Get query set to be used with django serializer
    # and create comment dict from comment's fields
    comment_query = Comment.objects.filter(pk=comment.pk)
    comment_dict = json.loads(serialize('json', comment_query))[0]['fields']
    comment_dict.update({'comment_id': json.loads(serialize('json', comment_query))[0]['pk']})

    # Remove null values
    comment_dict = {k: v for (k, v) in comment_dict.items() if v is not None}
    return comment_dict


def from_iso(date_string):
    """Custom parser function converting ISO date to datetime object"""
    try:
        return datetime(day=int(date_string.split('-')[2]),
                        month=int(date_string.split('-')[1]),
                        year=int(date_string.split('-')[0]),
                        tzinfo=timezone.get_fixed_timezone(timedelta(hours=2)))
    except Exception as e:
        raise e
