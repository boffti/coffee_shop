import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
Uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()


# ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = [drink.short() for drink in Drink.query.all()]
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except Exception:
        abort(404)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(jwt):
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
        return jsonify({
            'success': True,
            'drinks': drinks,
        })
    except Exception:
        abort(404)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    data = request.get_json()
    try:
        drink = Drink(title=data['title'], recipe=json.dumps(data['recipe']))
        Drink.insert(drink)
        drinks = [drink.long() for drink in Drink.query.all()]
        response = {
            "success": True,
            "drinks": drinks
        }
        return jsonify(response)
    except Exception:
        abort(422)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    drink = Drink.query.get(id)
    if drink:
        try:
            data = request.get_json()
            if 'title' in data:
                setattr(drink, 'title', data['title'])
            if 'recipe' in data:
                setattr(drink, 'recipe', json.dumps(data['recipe']))
            Drink.update(drink)
            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            })
        except Exception:
            abort(422)
    else:
        abort(401)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    drink = Drink.query.get(id)
    if drink:
        try:
            drink.delete()
            return jsonify({
                'success': True,
                'delete': id
            })
        except Exception:
            abort(422)
    else:
        abort(404)


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify(e.error), e.status_code
