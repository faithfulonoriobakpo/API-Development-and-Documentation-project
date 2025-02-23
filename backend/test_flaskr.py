import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category

from dotenv import load_dotenv
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_TEST = os.getenv('DB_TEST')

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = DB_TEST
        self.database_path = "postgresql://{}/{}".format(DB_HOST, self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_paginate_questions(self):
        response = self.client().get('/questions')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['success'], True)
        self.assertTrue(response_data['total_questions'])
        self.assertTrue(len(response_data['categories']))
        self.assertTrue(len(response_data['questions']))

    def test_404_page_nonexistent(self):
        response = self.client().get('/questions?page=1000')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Bad request')

    def test_get_categories(self):
        response = self.client().get('/categories')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['success'], True)
        self.assertTrue(len(response_data['categories']))

    def test_404_get_categories_error(self):
        response = self.client().get('/categories/100000')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Page not found')

    def test_get_questions(self):
        response = self.client().get('/questions')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['success'], True)
        self.assertTrue(response_data['total_questions'])
        self.assertTrue(len(response_data['questions']), 10)
        self.assertTrue(response_data['categories'])


    def test_delete_questions(self):
        question = Question(
            question='Test question',
            answer='Test answer',
            difficulty=1,
            category=1
            )

        question.insert()
        id = question.id

        response = self.client().delete(f'/questions/{id}')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['success'], True)
        self.assertEqual(response_data['deleted'], id)

    def test_422_question_nonexistent(self):
        response = self.client().delete('/questions/1000')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Unprocessable resource')

    def test_post_questions(self):
        response = self.client().post('/questions', json={
                                            'question': 'Test question',
                                            'answer': 'Test answer',
                                            'category': 1,
                                            'difficulty': 1
                                        })
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['success'], True)

    def test_422_post_question_error(self):
        response = self.client().post('/questions', json={
                                            'question': 'Test question',
                                            'answer': 'Test answer',
                                            'category': 19,
                                            'difficulty': 1
                                        })
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Unprocessable resource')

    def test_search_questions(self):
        response = self.client().post('/questions/search', json={
            'searchTerm': 'Who'
        })
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['success'], True)
        self.assertIsNotNone(response_data['questions'])
        self.assertIsNotNone(response_data['total_questions'])

    def test_404_search_questions_error(self):
        response = self.client().post('/questions/search', json={
            'searchTerm': 'sfsiku dusofu'})
        response_data = json.loads(response.data)

        self.assertEqual(response_data['success'], False)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_data['message'], 'Unprocessable resource')

    def test_get_categories_questions(self):
        response = self.client().get('/categories/1/questions')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['success'], True)
        self.assertTrue(len(response_data['questions']))
        self.assertTrue(response_data['total_questions'])
        self.assertTrue(response_data['current_category'])

    def test_404_get_categories_questions_error(self):
        response = self.client().get('/categories/1000/questions')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Bad request')

    def test_get_quiz_questions(self):
        response = self.client().post('/quizzes', json={
            'quiz_category': {'type': 'Entertainment', 'id': '3'},
            'previous_questions': []
        })
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['success'], True)
        self.assertTrue(response_data['question'])

    def test_500_get_quiz_questions(self):
        response = self.client().post('/quizzes', json={'previous_questions': []})
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Internal server error. Please try again later.')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()