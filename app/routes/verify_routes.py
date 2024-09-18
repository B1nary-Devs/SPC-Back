from flask import Blueprint, request, jsonify
from app import mongo
from datetime import datetime


verify = Blueprint('verify', __name__)

