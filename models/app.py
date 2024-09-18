import os
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from pymongo import MongoClient

mongo = PyMongo()

def create_app():
    app = Flask(__name__)

    mongo_username = os.environ.get('MONGODB_USERNAME', 'spcFlask')
    mongo_password = os.environ.get('MONGODB_PASSWORD', 'admin')
    mongo_hostname = os.environ.get('MONGODB_HOSTNAME', 'mongo')
    mongo_database = os.environ.get('MONGODB_DATABASE', 'spc')

    mongo_uri = f"mongodb://{mongo_username}:{mongo_password}@{mongo_hostname}:27017/spc"

    # client = MongoClient(mongo_uri)
    # db = client.get_database(mongo_database)

    app.config["MONGO_URI"] = mongo_uri
    mongo.init_app(app)

    # Importar e registrar blueprints (rotas)
    from .routes.user_routes import userRoute
    from .routes.term_routes import termRoute
    from .routes.user_term_routes import userTermRoute
    # from .routes.verify_routes import verify

    app.register_blueprint(userRoute(), url_prefix='/users')
    app.register_blueprint(termRoute(), url_prefix='/terms')
    app.register_blueprint(userTermRoute(), url_prefix='/user_terms')
    # app.register_blueprint(verify, url_prefix='/verify')

    return app