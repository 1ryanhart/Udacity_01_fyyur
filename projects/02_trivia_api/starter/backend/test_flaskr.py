import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "postgres", "", "localhost:5432", self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_category_with_result(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['categories']), 6)

    def test_get_question_search_without_results(self):
        res = self.client().get('/questions', json={'search':'noacvxcsdsadl'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'], 0)
        self.assertTrue(len(data['questions']), 0)

    def test_get_question_search_with_results(self):
        res = self.client().get('/questions', json={'search':'autobiography'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']), 1)

    def test_delete_question_without_results(self):
        res = self.client().delete('/questions/10000')
        data = json.loads(res.data)
        question = Question.query.get(10000)

        self.assertIsNone(question)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'resource not found')

    def test_delete_question_with_results(self):
        new_question = Question(question='test question to delete', answer='to delete', difficulty=1,category=4)
        new_question.insert()
        new_id_to_delete=Question.query.filter(Question.question=='test question to delete').first().id
        res = self.client().delete(f'/questions/{new_id_to_delete}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

    def test_get_seach_category_questions_with_results(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['total_questions'])
        self.assertTrue(len(data['questions']), 10)

    def test_get_seach_category_questions_without_results(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'resource not found')

    def test_post_quiz_with_results(self):
        res = self.client().post("/quizzes", json= {
            'previous_questions': [],
            'quiz_category': {'type': 'History', 'id': '4'},
            'categories': {'1': 'Science', '2': 'Art', '3': 'Geography', '4': 'History', '5': 'Entertainment', '6': 'Sports'}
                                                    }
                                )
        data = json.loads(res.data)

    def test_post_quiz_without_results(self):
        res = self.client().post("/quizzes", json= {
            'previous_questions': [],
            'quiz_category': {'type': 'Not_existing_cat', 'id': '4000'},
            'categories': {'1': 'Science', '2': 'Art', '3': 'Geography', '4': 'History', '5': 'Entertainment', '6': 'Sports'}
                                                    }
                                )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertIsNotNone(data['message'], 'unprocessable')

    def test_post_question(self):
        res = self.client().post('/questions', json = {
            'question':'test_post_question_question',
            'answer': 'test_post_question_answer',
            'difficulty': '5',
            'category': '2'
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        new_question = Question.query.filter(Question.question=='test_post_question_question').first()
        new_question.delete()

    def test_post_question_error(self):
        res = self.client().post('/questions', json = {})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
