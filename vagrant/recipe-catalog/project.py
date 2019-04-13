from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

from models import Base, User, Recipe

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Recipe App"


# Connect to Database and create database session
engine = create_engine('sqlite:///recipes.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#
#
#
#  Start Login, Auth Section
#
#
#


# Create anti-forgery state token
@app.route('/login/')
def showLogin():
    # Create anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'
        .format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if not create new user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    return output

# User Helper Functions


def createUser(login_session):
    session = DBSession()
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
        )
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    session = DBSession()
    return session.query(User).filter_by(id=user_id).one()


def getUserID(email):
    session = DBSession()
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None

# --------------------------END LOG IN ROUTES ----------------------------

# --------------------------BEGIN LOG OUT ROUTES --------------------------


@app.route('/gdisconnect')
def gdisconnect():
    # only disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    # execute HTTP GET request to revoke current token
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # reset the user's session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    else:
        # token given is invalid
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

#
#
#
# --------------------------END Auth ROUTES ----------------------------
#
#
#


#
#
#
# --------------------------Start JSON Endpoints----------------------------
#
#
#

# View All recipes JSON
@app.route('/recipes.json/')
def recipesJSON():
    recipes = session.query(Recipe).all()
    return jsonify(
        recipes=[r.serialize for r in recipes]
    )


# View Users
@app.route('/users.json/')
def usersJSON():
    users = session.query(User).all()
    return jsonify(
        users=[r.serialize for r in users]
    )


#
#
#
# --------------------------End JSON Endpoints----------------------------
#
#
#


#
#
#
# --------------------------Start Recipe App Routes----------------------------
#
#
#

# Show all recipes
@app.route('/', methods=['GET', 'POST'])
@app.route('/recipes/', methods=['GET', 'POST'])
def showRecipes():
    recipes = session.query(Recipe).order_by(asc(Recipe.name))
    # TODO: Uncomment once login issues are fixed
    # if 'username' not in login_session:
    #     return render_template('publicRecipes.html', recipes = recipes)
    if request.method == 'POST':
        recipeToDelete = session.query(Recipe).filter_by(
            id=request.form['delete']).one()
        session.delete(recipeToDelete)
        session.commit()
        return redirect(url_for('showRecipes'))
    else:
        return render_template('recipes.html', recipes=recipes)


# Show specific category recipes
@app.route('/recipes/<recipe_category>/')
def showCategory(recipe_category):
    recipesInCategory = session.query(Recipe).filter_by(
        category=recipe_category).all()
    # TODO: Uncomment once login issues are fixed
    # if 'username' not in login_session:
    #     return render_template(
    #       'publicRecipesInCategory.html',
    #       recipesInCategory=recipesInCategory
    #   )
    # else:
    return render_template(
        'recipesInCategory.html', recipesInCategory=recipesInCategory
        )


# Show specific recipe
@app.route('/recipes/<int:recipe_id>/')
def showSingleRecipe(recipe_id):
    recipe = session.query(Recipe).filter_by(id=recipe_id).one()
    # TODO: Uncomment once login issues are fixed
    # if 'username' not in login_session:
    #     return render_template('publicViewRecipe.html', recipe = recipe)
    # else:
    return render_template('viewRecipe.html', recipe=recipe)


# Create a New Recipe
@app.route('/recipes/new/', methods=['GET', 'POST'])
def newRecipe():
    # TODO: Uncomment once login issues are fixed
    # if 'username' not in login_session:
    # return redirect('/login')
    if request.method == 'POST':
        newRecipe = Recipe(
            name=request.form['name'],
            category=request.form['category'],
            cook_time=request.form['cook_time'],
            instructions=request.form['instructions'],
            ingredients=request.form['ingredients'],
            # picture = request.form['picture'],
            # user_id = login_session['user_id']
        )
        session.add(newRecipe)
        session.commit()
        return redirect(url_for('showRecipes'))
    else:
        return render_template('newRecipe.html')


# Edit a Recipe
@app.route('/recipes/<int:recipe_id>/edit', methods=['GET', 'POST'])
def editRecipe(recipe_id):
    editedRecipe = session.query(Recipe).filter_by(id=recipe_id).one()
    # TODO: Uncomment once login issues are fixed
    # if 'username' not in login_session:
    #     return redirect('/login')
    # if editedRecipe.user_id != login_session['user_id']:
    #     return """
    #         <script>
    #             function myFunction() {
    #                 alert(
    #                     '''
    #                       You are not authorized to edit this recipe.
    #                       Please create your own recipe in order to edit.
    #                     '''
    #                     );
    #                 }
    #         </script>
    #         <body onload='myFunction()''>
    #     """
    # FIXME post method isn't actually saving to DB
    if request.method == 'POST':
        if request.form['name']:
            editedRecipe.name = request.form['name']
        if request.form['category']:
            editedRecipe.category = request.form['category']
        if request.form['cook_time']:
            editRecipe.cook_time = request.form['cook_time']
        if request.form['ingredients']:
            editRecipe.ingredients = request.form['ingredients']
        if request.form['instructions']:
            editRecipe.instructions = request.form['instructions']
        # if request.form['picture']:
        #     editedRecipe.picture = request.form['picture']
        session.add(editedRecipe)
        session.commit()
        return redirect(url_for('showRecipes'))
    else:
        return render_template('editRecipe.html', recipe=editedRecipe)


# Delete a recipe
@app.route('/recipes/<int:recipe_id>/delete/', methods=['GET', 'POST'])
def deleteRecipe(recipe_id):
    recipeToDelete = session.query(Recipe).filter_by(id=recipe_id).one()
    # TODO: Uncomment once login issues are fixed
    # if 'username' not in login_session:
    #     return redirect('/login')
    # if recipeToDelete.user_id != login_session['user_id']:
    #     return """
    #         <script>
    #             function myFunction() {
    #                 alert(
    #                     '''
    #                       You are not authorized to delete this recipe.
    #                       Please create your own recipe.
    #                     '''
    #                 );
    #             }
    #         </script>
    #         <body onload='myFunction()''>
    #     """
    if request.method == 'POST':
        session.delete(recipeToDelete)
        session.commit()
        return redirect(url_for('showRecipes'))
    else:
        return render_template('deleteRecipe.html', recipe=recipeToDelete)

#
#
#
# -----------------------------END Recipe Routes-------------------------------
#
#
#


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)