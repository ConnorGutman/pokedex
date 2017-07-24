import json
import requests
import urllib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from createDB import Type, Pokemon, User, Base

# Connect to the db and wipe all existing data
engine = create_engine('sqlite:///pokedex.db')
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# configure from createDB.py
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Make a new user named Ash Ketchum
ash = User(name="Ash Ketchum", email="ashketchum@gmail.com")
session.add(ash)
session.commit()

# Scrape API for Pokemon data!
# (Data courtesy of https://pokeapi.co/)
pokemonTypes = []
pokemonNames = []
pokemonPages = []
pokemonSprites = []
pokemonBios = []

for i in range(1, 19):
    url = 'http://pokeapi.co/api/v2/type/' + str(i) + '/'
    print 'hitting ' + url
    resp = requests.get(url=url)
    data = json.loads(resp.text)
    pokemonTypes.append(data["name"])
    pokemonNames.append(data["pokemon"][0]["pokemon"]["name"])
    pokemonNames.append(data["pokemon"][1]["pokemon"]["name"])
    pokemonNames.append(data["pokemon"][2]["pokemon"]["name"])
    pokemonPages.append((data["pokemon"][0]["pokemon"]["url"])[32:])
    pokemonPages.append((data["pokemon"][1]["pokemon"]["url"])[32:])
    pokemonPages.append((data["pokemon"][2]["pokemon"]["url"])[32:])

for i in range(0, len(pokemonPages)):
    url = 'http://pokeapi.co/api/v2/pokemon-species' + str(pokemonPages[i])
    print 'hitting ' + url
    resp = requests.get(url=url)
    data = json.loads(resp.text)
    pokemonBios.append(data["flavor_text_entries"][1]["flavor_text"])

for i in range(0, len(pokemonPages)):
    url = 'http://pokeapi.co/api/v2/pokemon' + str(pokemonPages[i])
    print 'hitting ' + url
    resp = requests.get(url=url)
    data = json.loads(resp.text)
    urllib.urlretrieve(data["sprites"]["front_default"],
                       './static/sprites/' + str(data["name"]) + '.png')

for i in range(0, len(pokemonTypes)):
    type = Type(name=pokemonTypes[i], user_id=1)
    pokemon1 = Pokemon(name=pokemonNames[(i * 3)], user_id=1,
                       bio=pokemonBios[(i * 3)],
                       sprite='/static/sprites/' +
                       str(pokemonNames[(i * 3)]) + '.png',
                       type=type)
    pokemon2 = Pokemon(name=pokemonNames[(i * 3) + 1], user_id=1,
                       bio=pokemonBios[(i * 3) + 1],
                       sprite='/static/sprites/' +
                       str(pokemonNames[(i * 3) + 1]) + '.png',
                       type=type)
    pokemon3 = Pokemon(name=pokemonNames[(i * 3) + 2], user_id=1,
                       bio=pokemonBios[(i * 3) + 2],
                       sprite='/static/sprites/' +
                       str(pokemonNames[(i * 3) + 2]) + '.png',
                       type=type)
    session.add(type)
    session.add(pokemon1)
    session.add(pokemon2)
    session.add(pokemon3)
    session.commit()

print 'Demo pokemon successfully registered to the pokedex!'
