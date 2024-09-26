from flask import Blueprint, request, jsonify
from models.app import mongo


verify = Blueprint('verify', __name__)
users_collection = mongo.db.usuario #colecao de usuarios do mongo db
terms_collection = mongo.db.termo

