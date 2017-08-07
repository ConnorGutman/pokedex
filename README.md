# Udacity Pokedex

A fun and basic Pokedex built for the Udacity Item Catalog assignment. Gives a list of pokemon organized by different types. Includes JSON endpoints and third party user registration. Enjoy!

## Getting Started

1. Clone [this repository](https://github.com/connorgutman/pokedex) into the *catalog* directory found within the [fullstack-nanodegree-vm repository](https://github.com/udacity/fullstack-nanodegree-vm) provided by Udacity for this nanodegree.

2. (optional) Follow the "Getting started" portion of [Udacity's instructions for this project](https://docs.google.com/document/d/1jFjlq_f-hJoAZP8dYuo5H3xY62kGyziQmiv9EPIA7tM/pub?embedded=true) if you'd like to use vagrant.

## Running the Pokedex

If this is your first time running the Pokedex, start by populating the database with some demo pokemon data:

`python demopokemon.py`

This will take several minutes to scrape the amazing and free [PokeApi.co](https://pokeapi.co/) for some demo Pokemon.

After populating the database with some initial Pokemon, run the Pokedex with the following command:

`python pokedex.py`

Finally, navigate to:

`http://localhost:5000/`


## Endpoints:
* `/` Most recent Pokemon
* `/JSON` JSON endpoint for all Pokemon types
* `/type(EX:water)` Lists all Pokemon of a given type
* `/type/JSON` JSON endpoint for all Pokemon of a given type
* `/type/id` View a specific Pokemon
* `/type/id/JSON` JSON endpoint for a specific pokemon
* `/type/id/edit` Edit a Pokemon that you submitted
* `/type/id/delete` Delete a Pokemon that you submitted
* `/login` Log-In using Google
* `/logout` Log-Out
