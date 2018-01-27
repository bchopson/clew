# Clew

A Clue (Cluedo) assistant using the picosat SAT solver

Implemented as a Flask API with a MongoDB data store.

## Theory

This project is a Python implementation of the Clue project from  
undergraduate artificial intelligence coursework at Gettysburg College.  
See http://cs.gettysburg.edu/~tneller/nsf/clue/

Player knowledge about Clue is encoded as boolean variables. This knowledgebase  
is fed into an SAT solver (picosat) after each turn in order to produce a  
"detective notebook" to aid the human player in his or her deductions.

## Getting Started

1. Create a Python 3 virtualenv for the project.
2. Run `pip install requirements.txt`
3. Set environment variable `DATABASE` to a MongoDB instance of your choice.
4. Set environment variable `FLASK_APP` to `clew/app.py`.
5. `flask run` to run the server
6. An API client is available at https://github.com/bchopson/clew-app

*Note: setting environment variables can be automated with autoenv.*

## Running the tests

Run `pytest`  
See `/tests` directory

## License

This project is licensed under the MIT License - see the LICENSE.md file for details
