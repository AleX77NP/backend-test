from flask import Blueprint, jsonify, session, redirect
from .models import Aranzman

main = Blueprint('main', __name__)

@main.route('/')
def main_index():
    return 'Hello World'

@main.route('/api/aranzmani')
def aranzmani():
    aranzmani = Aranzman.query.all()
    return jsonify(aranzmani)

@main.route("/login/<korisnik>", methods=["POST", "GET"])
def login(korisnik):
    session['korisnik'] = korisnik
    return jsonify({'message': 'Log in'})

@main.route("/home")
def home():
  # check if the users exist or not
    if not session.get("korisnik"):
        # if not there in the session then redirect to the login page
        return redirect('/')
    return jsonify({'korisnik': session.get('korisnik')})

@main.route("/logout")
def logout():
    session.pop('korisnik')
    return jsonify({'message': 'Log out'})