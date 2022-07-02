import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    CORS set up. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={'/': {'origins': '*'}})

    """
    After_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, PUT, POST, DELETE, OPTIONS')
        return response

    """
    An endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        category_obj = {}

        for category in categories:
            category_obj[category.id] = category.type

        if (len(category_obj) == 0):
            abort(404)

        return jsonify({
                'success': True,
                'categories': category_obj
            })

    """
    An endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    """
    @app.route('/questions')
    def get_questions():
        try:
            #get and paginate all questions
            select_list = Question.query.all()
            total_questions = len(select_list)
            current_questions = paginate_questions(request, select_list)

            #fetch all categories
            categories = Category.query.all()
            category_obj = {}
            for category in categories:
                category_obj[category.id] = category.type

            # abort if nothing is found
            if (len(current_questions) == 0):
                abort(404)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': total_questions,
                'categories': category_obj
            })
        except Exception as error:
            print(error)
            abort(400)

    """
    An endpoint to DELETE question using a question ID.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter_by(id=id).one_or_none()
            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': id
            })

        except Exception as error:
            print(error)
            abort(422)

    """
    An endpoint to POST a new question,
    which requires the question and answer text,
    category, and difficulty score.
    """

    @app.route("/questions", methods=['POST'])
    def post_question():
        
        response = request.get_json()

        new_question = response.get('question')
        new_answer = response.get('answer')
        new_category = response.get('category')
        new_difficulty = response.get('difficulty')

        try:
            question = Question(question=new_question, answer=new_answer,
                                category=new_category, difficulty=new_difficulty)

            question.insert()

            questions_select_list = Question.query.all()
            current_questions = paginate_questions(request, questions_select_list)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(questions_select_list)
            })

        except Exception as error:
            print(error)
            abort(422)



    """
    A POST endpoint to get questions based on a search term.
    """
    @app.route('/questions/search', methods=['GET','POST'])
    def search_questions():
        response = request.get_json()

        if(response['searchTerm']):
            search_term = response['searchTerm']

        questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()

        if questions==[]:
            abort(404)

        result = paginate_questions(request, questions)

        return jsonify({
            'success': True,
            'questions': result,
            'total_questions': len(questions)
        })

    """
    A GET endpoint to get questions based on category.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_category_questions(id):
        category = Category.query.get(id)
        if (category is None):
            abort(400)

        try:
            questions = Question.query.filter_by(category=category.id).all()
            current_questions = paginate_questions(request, questions)

            return jsonify({
            'success': True,
            'questions': current_questions,
            'current_category': category.type,
            'total_questions': len(Question.query.all())
            })
        except:
            abort(500)

    """
    A POST endpoint to get questions to play the quiz.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        response = request.get_json()
        previous_question = response.get('previous_questions')
        category = response.get('quiz_category')

        if ((category is None) or (previous_question is None)):
                abort(400)

        try:
            if (category['id'] == 0):
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(category=category['id']).all()

            
            randomIndex = random.randint(0, len(questions)-1)
            next_question = questions[randomIndex]

            while next_question.id not in previous_question:
                next_question = questions[randomIndex]
                return jsonify({
                    'success': True,
                    'question': {
                        "answer": next_question.answer,
                        "category": next_question.category,
                        "difficulty": next_question.difficulty,
                        "id": next_question.id,
                        "question": next_question.question
                    },
                    'previous_question': previous_question
                })

        except Exception as error:
            print(error)
            abort(404)


    """
    error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Page not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable_resource(error):
        return jsonify({
            'success': False,
            'error': 422, 
            'message': 'Unprocessable resource'
        }), 422

    @app.errorhandler(500)
    def internal_server(error):
        return jsonify({
            'success': False,
            'error': 500, 
            'message': 'Internal server error. Please try again later.'
        }), 500

    return app
