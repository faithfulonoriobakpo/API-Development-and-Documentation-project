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
            'categories': categories_obj
        })

    """
    An endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    """
@app.route()
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

    new_question = response['question']
    new_answer = response['answer']
    new_category = response['category']
    new_difficulty = response['difficulty']

    try:
        question = Question(question=new_question, answer=new_answer,
                            category=new_category, difficulty=new_difficulty)

        question.insert()

        questions_select_list = Question.query.all()
        current_questions = paginate_questions(request, selection)

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
#search related question with input string
    response = request.get_json()

    if(data['searchTerm']):
        search_term = response['searchTerm']

    related_questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()

    if related_questions==[]:
        abort(404)

    output = paginate_questions(request, related_questions)

    return jsonify({
        'success': True,
        'questions': output,
        'total_questions': len(related_questions)
    })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

