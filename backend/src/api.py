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

#POST DRINK
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
        abort(422)

#PATCH DRINK
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
        abort(422)

#DELETE DRINK
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
        abort(422)

# Error Handling

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
        "message": "resource not found"}), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422, 
        "message": "unprocessable"}), 422,

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400, 
        "message": "bad request"}), 400

@app.errorhandler(405)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404, 
        "message": "method not allowed"}), 404
    

@app.errorhandler(401)
def  unauthorizaion_required(error):
    raise AuthError({
                "success": False,
                "description": "Authorization required",
                "error": 401
            }, 401)

@app.errorhandler(403)
def  not_unauthorized(error):
    raise AuthError({
                "success": False,
                "description": "Unauthorized operation",
                "error": 403
            }, 403)
