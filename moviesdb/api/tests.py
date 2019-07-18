from django.test import Client, TestCase


class APIEndpointsTest(TestCase):
    """Basic tests of the API endpoints"""

    # Fixtures for test database
    fixtures = ['movie.json', 'rating.json', 'comment.json']

    def setUp(self):
        self.client = Client()

    def test_movies_get(self):
        """Get all movies"""

        response = self.client.get('/api/movies/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), list))
        self.assertTrue(len(response.json()) == 4)

    def test_movies_post_valid_titles(self):
        """Post movie with valid title not present in db"""

        titles = ['Robot Monster',
                  'The Creeping Terror',
                  'Nukie']
        for title in titles:
            response = self.client.post('/api/movies/', {'title': title})
            self.assertEqual(response.status_code, 201, title)
            self.assertFalse(response.json().get('error'), title)

    def test_movies_post_used_titles(self):
        """Post movie with valid title present in db"""

        titles = ['The Incredibly Strange Creatures Who Stopped Living and Became Mixed-Up Zombies',
                  'Plan 9 from Outer Space',
                  'Dünyayı Kurtaran Adam',
                  'Matango']
        for title in titles:
            response = self.client.post('/api/movies/', {'title': title})
            self.assertEqual(response.status_code, 409, title)
            self.assertTrue(response.json().get('error'), title)

    def test_movies_post_invalid_titles(self):
        """Post movie with invalid title"""

        titles = ['Horsenado',
                  'The Shroom',
                  'Battlefield Perth']
        for title in titles:
            response = self.client.post('/api/movies/', {'title': title})
            self.assertEqual(response.status_code, 404, title)
            self.assertTrue(response.json().get('error'), title)

    def test_comments_get(self):
        """Get all comments"""

        response = self.client.get('/api/comments/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), list))
        self.assertTrue(len(response.json()) == 5)

    def test_comments_get_by_movie_id(self):
        """Get comments for specific movie ID"""

        response = self.client.get('/api/comments/?movie_id=1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), list))
        self.assertTrue(len(response.json()) == 1)

    def test_comments_post_valid(self):
        """Post comment with valid data"""

        comments = [{"movie_id": 1, "comment_body": "The best movie I've ever seen"},
                    {"movie_id": 2, "comment_body": "The best movie I've ever seen"},
                    {"movie_id": 3, "comment_body": "The best movie I've ever seen"}]
        for comment in comments:
            response = self.client.post('/api/comments/', comment)
            self.assertEqual(response.status_code, 201, comment)
            self.assertFalse(response.json().get('error'), comment)

    def test_comments_post_invalid(self):
        """Post comment with invalid data"""

        comments = [{"movie_id": 5, "comment_body": "The best movie I've ever seen"},
                    {"movie_id": 2},
                    {}]
        for comment in comments:
            response = self.client.post('/api/comments/', comment)
            self.assertEqual(response.status_code, 400, comment)
            self.assertTrue(response.json().get('error'), comment)

    def test_top_valid(self):
        """
        Get movies list ranked by comments count
        Only comments added in specified, valid date range are counted
        """

        response = self.client.get('/api/top/?date_start=2019-07-10&date_end=2019-07-16')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), list))
        self.assertTrue(len(response.json()) == 4)

    def test_top_invalid(self):
        """
        Get movies list ranked by comments count
        with invalid/missing date range parameters
        """

        parameters = [{'date_start': '2019-01-01', 'date_end': '2019-01-0l'},
                      {'date_start': '2019-01-01'},
                      {'date_start': '2019-01-01', 'date_end': '1'}]
        for params in parameters:
            url = '/api/top/?date_start={0}&date_end={1}'.format(params.get('date_start', ''),
                                                                 params.get('date_end', ''))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 400)
            self.assertTrue(response.json().get('error'))
