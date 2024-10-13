import os
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from flasgger import Swagger

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    CORS(app)
    swagger = Swagger(app, template_file='../swagger_config.json')
    
    app.config["MONGO_URI"] = f'mongodb://{os.environ.get("MONGODB_HOSTNAME", "mongo")}:27017/{os.environ.get("MONGODB_DATABASE", "spc")}'
    mongo.init_app(app)

    # Importar e registrar blueprints (rotas)
    from .routes.user_routes import user
    from .routes.term_routes import term
    from .routes.assignee_routes import assignee
    from .routes.user_term_routes import user_term
    from .routes.verify_routes import verify

    app.register_blueprint(user, url_prefix='/users')
    app.register_blueprint(term, url_prefix='/terms')
    app.register_blueprint(user_term, url_prefix='/user_terms')
    app.register_blueprint(verify, url_prefix='/verify')
    app.register_blueprint(assignee, url_prefix='/assignee')


    return app