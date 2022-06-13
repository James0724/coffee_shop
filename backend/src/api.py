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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
#db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
#GET DRINKS
@app.route("/drinks")
def get_drinks_short():
    drinks = [drink.short() for drink in Drink.query.all()]
    #print('drink_short:', drinks)

    if len(drinks) == 0:
            abort(404)

    return jsonify(
        {
            "success": True,
            "drinks": drinks,
        }
    )

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
#GET DRINK DETAILS
@app.route('/drinks-details')
@requires_auth('get:drinks-details')
def get_drinks_long():
    drinks = [drink.long() for drink in Drink.query.all()]
    #print('drink_long:', drinks)

    if len(drinks) == 0:
            abort(404)

    return jsonify(
        {
            "success": True,
            "drinks": drinks,
        }
    )

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"])
@requires_auth('post:drinks')
def create_new_drink():
    body = request.get_json()

    new_drink_title = body['title']
    new_drink_recipe =json.dumps(body['recipe'])

    

    try:
   
        drink = Drink( title= new_drink_title, recipe=new_drink_recipe)
        drink.insert()

        return jsonify(
            {
            "success": True,
            "drink": body
        
        }
        )

    except Exception as e:
        print(e)
        return jsonify(
            {"success": False,
            "error":422
            }
            )
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<id>", methods=["PATCH"])
@requires_auth('patch:drinks')
def edit_new_drink(id):
    drink  = Drink.query.get_or_404(id)
    
    body = json.loads(request.data)
    new_drink_title = body['title']
    new_drink_recipe =json.dumps(body['recipe'])
    try:
        drink.title = new_drink_title
        drink.recipe = new_drink_recipe
        drink.insert()
    

        return jsonify(
            {
            "success": True,
            "title": drink.title,
            "recipe": json.loads(drink.recipe)
        }
        )

    except Exception as e:
        print(e)
        return jsonify(
            {"success": False,
            "error":422
            }
            )

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_new_drink(id):
    delete_drink  = Drink.query.get_or_404(id)

    try:
        Drink.delete(delete_drink)

        return jsonify(
            {
            "success": True,
            "deleted": id,
        }
        )

    except Exception as e:
        print(e)
        return jsonify(
            {"success": False,
            "error": 422
            }
            )

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


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
        404,
    )

@app.errorhandler(422)
def unprocessable(error):
    return (
        jsonify({"success": False, "error": 422, "message": "unprocessable"}),
        422,
    )

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

@app.errorhandler(405)
def not_found(error):
    return (
        jsonify({"success": False, "error": 405, "message": "method not allowed"}),
        405,
    )

@app.errorhandler(401)
def  unauthorizaion_required(error):
    raise AuthError({
                "success": False,
                "description": "Authorization required.",
                "error": 401
            }, 401)

@app.errorhandler(403)
def  not_unauthorized(error):
    raise AuthError({
                "success": False,
                "description": "Unauthorized operation.",
                "error": 403
            }, 403)
'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
