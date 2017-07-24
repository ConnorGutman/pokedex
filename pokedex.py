import os
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    redirect,
    jsonify,
    flash,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from createDB import (
    Base,
    Type,
    Pokemon,
    User,
)
from flask import session as login_session
import random
import string
import httplib2
import requests
from oauth2client.client import (
    flow_from_clientsecrets
)
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './static/sprites'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Connect to DB ===============================================================

pokedexDB = create_engine('sqlite:///pokedex.db')
Base.metadata.bind = pokedexDB
PokedexConnect = sessionmaker(bind=pokedexDB)
session = PokedexConnect()


# Homepage ====================================================================
@app.route('/')
def listTypes():
    types = session.query(Type).all()
    pokemons = session.query(Pokemon).all()

    return render_template('types.html', types=types,
                           pokemons=pokemons, pageType='homepage')


# Json for homepage
@app.route('/JSON')
def listTypesJSON():
    types = session.query(Type).all()
    return jsonify(types=[type.serialize for type in types])


# Pokemon types ===============================================================
@app.route('/<string:pokedex_id>')
def listType(pokedex_id):
    # List out all Pokemon types
    types = session.query(Type).all()
    try:
        type = session.query(Type).filter_by(name=pokedex_id).first()
        typeName = type.name
    except:
        typeName = ' '
    # Get all pokemon for current type
    pokemons = session.query(Pokemon).filter_by(
        type_id=pokedex_id).all()
    pokemonsCount = session.query(
        Pokemon).filter_by(type_id=pokedex_id).count()

    return render_template('types.html', types=types,
                           pokemons=pokemons,
                           typeName=typeName,
                           pokemonsCount=pokemonsCount,
                           pageType='typepage')


# JSON for all pokemon of a certain type
@app.route('/<string:pokedex_id>/JSON')
def listTypeJSON(pokedex_id):
    pokemons = session.query(Pokemon).filter_by(
        type_id=pokedex_id).all()
    return jsonify(pokemons=[pokemon.serialize for pokemon in
                             pokemons])


# Individual Pokemon page =====================================================
@app.route('/<string:pokedex_id>/<int:pokemon_id>')
def listPokemon(pokedex_id, pokemon_id):
    # Get types
    types = session.query(Type).all()
    pokemon = session.query(Pokemon).filter_by(id=pokemon_id).first()
    # Get trainer who discovered pokemon
    print pokemon.user_id
    trainer = session.query(User).filter_by(id=pokemon.user_id).one()

    return render_template('pokemon.html', types=types,
                           pokemon=pokemon, trainer=trainer)


# JSON for individual pokemon
@app.route('/<string:pokedex_id>/<int:pokemon_id>/JSON')
def listPokemonJSON(pokedex_id, pokemon_id):
    pokemon = session.query(Pokemon).filter_by(id=pokemon_id).first()
    return jsonify(pokemon=[pokemon.serialize])


# Pokemon sprite upload =======================================================
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Add Pokemon page ============================================================
@app.route('/add', methods=['GET', 'POST'])
def addPokemon():
    # Logged in?
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        if not request.form['name'] or not request.form['bio']:
            flash('Could not register Pokemon to Pokedex. Missing info.')
            return redirect(url_for('addPokemon'))
        if not request.files['sprite']:
            flash('Could not register Pokemon to Pokedex. Missing sprite.')
            return redirect(url_for('addPokemon'))

        # Add sprite for Pokemon
        file = request.files['sprite']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Register new Pokemon
        newPokemon = Pokemon(name=request.form['name'],
                             bio=request.form[
                             'bio'],
                             sprite='/static/sprites/' +
                             filename,
                             type_id=request.form['type'],
                             user_id=login_session['user_id'])

        session.add(newPokemon)
        session.commit()

        return redirect(url_for('listTypes'))
    else:
        types = session.query(Type).all()
        return render_template('addPokemon.html', types=types)


# Edit Pokemon page ===========================================================
@app.route('/<string:pokedex_id>/<int:pokemon_id>/edit',
           methods=['GET', 'POST'])
def editPokemon(pokedex_id, pokemon_id):
    # Logged in?
    if 'username' not in login_session:
        return redirect('/login')

    pokemon = session.query(Pokemon).filter_by(id=pokemon_id).first()

    # Get trainer of pokemon
    trainer = session.query(User).filter_by(id=pokemon.user_id).one()

    # Check if logged in user is pokemon's trainer
    if trainer.id != login_session['user_id']:
        return redirect('/login')

    types = session.query(Type).all()

    if request.method == 'POST':
        if request.form['name']:
            pokemon.name = request.form['name']
        if request.form['bio']:
            pokemon.bio = request.form['bio']
        if request.form['type']:
            pokemon.type_id = request.form['type']
        if request.files['sprite']:
            file = request.files['sprite']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                pokemon.sprite = '/static/sprites/' + filename
        return redirect(url_for('listPokemon',
                                pokedex_id=pokemon.type_id,
                                pokemon_id=pokemon.id))
    else:
        return render_template('editPokemon.html', types=types,
                               pokemon=pokemon)


# Delete Pokemon page =========================================================
@app.route('/<string:pokedex_id>/<int:pokemon_id>/delete',
           methods=['GET', 'POST'])
def deletePokemon(pokedex_id, pokemon_id):
    # Logged in?
    if 'username' not in login_session:
        return redirect('/login')

    types = session.query(Type).all()
    pokemon = session.query(Pokemon).filter_by(id=pokemon_id).first()

    # Get trainer of pokemon
    trainer = session.query(User).filter_by(id=pokemon.user_id).one()

    # Check if logged in user is pokemon's trainer
    if trainer.id != login_session['user_id']:
        return redirect('/login')

    if request.method == 'POST':
        session.delete(pokemon)
        session.commit()
        return redirect(url_for('listType',
                                pokedex_id=pokemon.type_id))
    else:
        return render_template('deletePokemon.html',
                               pokemon=pokemon,
                               types=types)


# Login page =================================================================
@app.route('/login')
def login():
    types = session.query(Type).all()
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    return render_template('login.html', STATE=state, types=types)


# Google auth for login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(request.data)
        login_session['access_token'] = credentials.access_token
        login_session['gplus_id'] = credentials.id_token['sub']
        answer = requests.get('https://www.googleapis.com/oauth2/v1/userinfo',
                              params={'access_token': credentials.access_token,
                                      'alt': 'json'})
        data = answer.json()
        login_session['username'] = data['name']
        login_session['email'] = data['email']
        login_session['provider'] = 'google'
        try:
            user_id = session.query(User).filter_by(email=data["email"]).one()
        except:
            user_id = None
        if not user_id:
            newUser = User(name=login_session['username'], email=login_session[
                           'email'])
            session.add(newUser)
            session.commit()
            u = session.query(User).filter_by(
                email=login_session['email']).one()
            user_id = u.id
        login_session['user_id'] = user_id
        return "Login Successful"
    except:
        return redirect('/login')


# Logout page ================================================================
@app.route('/logout')
def logout():
    if login_session['provider'] == 'google':
        gdisconnect()
        del login_session['gplus_id']
        del login_session['access_token']

    del login_session['username']
    del login_session['email']
    del login_session['user_id']
    del login_session['provider']

    return redirect(url_for('listTypes'))


# Google auth for logout
@app.route('/gdisconnect')
def gdisconnect():
    try:
        access_token = login_session.get('access_token')
        url = 'https://accounts.google.com/o/oauth2/revoke'
        params = '?token=%s' % access_token
        h = httplib2.Http()
        h.request(url + params, 'GET')[0]
    except:
        return redirect('/')


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5000)
