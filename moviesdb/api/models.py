from datetime import date

from django.db import models
from django.utils.timezone import now

# English abbreviations for months' names
# used in from_en_date parser function
MONTHS_ABBRV = ['',
                'Jan', 'Feb', 'Mar',
                'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep',
                'Oct', 'Nov', 'Dec']


class Movie(models.Model):
    title = models.CharField(max_length=200)
    year = models.CharField(max_length=200, blank=True, null=True)
    rated = models.CharField(max_length=200, blank=True, null=True)
    released = models.DateField(blank=True, null=True)
    runtime = models.CharField(max_length=200, blank=True, null=True)
    genre = models.CharField(max_length=200, blank=True, null=True)
    director = models.CharField(max_length=200, blank=True, null=True)
    writer = models.CharField(max_length=200, blank=True, null=True)
    actors = models.CharField(max_length=200, blank=True, null=True)
    plot = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=200, blank=True, null=True)
    awards = models.CharField(max_length=200, blank=True, null=True)
    poster = models.URLField(blank=True, null=True)
    metascore = models.SmallIntegerField(blank=True, null=True)
    imdb_rating = models.FloatField(blank=True, null=True)
    imdb_votes = models.IntegerField(blank=True, null=True)
    imdb_id = models.CharField(max_length=200, blank=True, null=True)
    item_type = models.CharField(max_length=200, blank=True, null=True)
    dvd = models.DateField(blank=True, null=True)
    box_office = models.IntegerField(blank=True, null=True)
    production = models.CharField(max_length=200, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    @classmethod
    def create_from_omdb_dict(cls, omdb_dict):
        movie = cls()

        # Null values marked as 'N/A' are removed from the omdb_dict
        cleaned_dict = dict()
        for key in omdb_dict:
            if omdb_dict[key] != 'N/A':
                cleaned_dict.update({key: omdb_dict[key]})
        omdb_dict = cleaned_dict

        # Setting instance attributes from the omdb_dict
        movie.title = omdb_dict.get('Title')
        movie.year = omdb_dict.get('Year')
        movie.rated = omdb_dict.get('Rated')
        try:
            movie.released = from_en_date(en_date=omdb_dict.get('Released'))
        except AttributeError:
            movie.released = None
        movie.runtime = omdb_dict.get('Runtime')
        movie.genre = omdb_dict.get('Genre')
        movie.director = omdb_dict.get('Director')
        movie.writer = omdb_dict.get('Writer')
        movie.actors = omdb_dict.get('Actors')
        movie.plot = omdb_dict.get('Plot')
        movie.language = omdb_dict.get('Language')
        movie.country = omdb_dict.get('Country')
        movie.awards = omdb_dict.get('Awards')
        movie.poster = omdb_dict.get('Poster')
        try:
            movie.metascore = int(omdb_dict.get('Metascore'))
        except TypeError:
            movie.metascore = None
        try:
            movie.imdb_rating = float(omdb_dict.get('imdbRating'))
        except TypeError:
            movie.imdb_rating = None
        try:
            movie.imdb_votes = int(omdb_dict.get('imdbVotes').replace(',', ''))
        except AttributeError:
            movie.imdb_votes = None
        movie.imdb_id = omdb_dict.get('imdbID')
        movie.item_type = omdb_dict.get('Type')
        try:
            movie.dvd = from_en_date(en_date=omdb_dict.get('DVD'))
        except AttributeError:
            movie.dvd = None
        try:
            movie.box_office = int(omdb_dict.get('BoxOffice').replace(',', '').replace('$', ''))
        except AttributeError:
            movie.box_office = None
        movie.production = omdb_dict.get('Production')
        movie.website = omdb_dict.get('Website')
        return movie

    def __str__(self):
        return self.title


class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    source = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

    @classmethod
    def create_from_rating_dict(cls, movie, rating_dict):
        rating = cls()

        # Setting instance attributes from the rating_dict
        rating.movie = movie
        rating.source = rating_dict.get('Source')
        rating.value = rating_dict.get('Value')
        return rating

    def __str__(self):
        return "{0}: {1} rating".format(self.movie.title, self.source)


class Comment(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    comment_body = models.TextField()
    added = models.DateTimeField(default=now)

    def __str__(self):
        return "Comment to: {0}. Comment's id: {1}".format(self.movie.title, self.pk)


def from_en_date(en_date):
    """
    Custom parser function converting localized
    English date (e.g. 01 Jul 2019) to date object
    """
    try:
        return date(day=int(en_date.split(' ')[0]),
                    month=MONTHS_ABBRV.index(en_date.split(' ')[1]),
                    year=int(en_date.split(' ')[2]))
    except Exception as e:
        raise e
