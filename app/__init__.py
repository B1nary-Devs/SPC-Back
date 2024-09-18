from flask import Flask
from flask_pymongo import PyMongo

mongo = PyMongo()

def create_app():
    app = Flask(__name__)

    # Configurações do MongoDB
    # app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
    # mongo.init_app(app)

    # Importar e registrar blueprints (rotas)
    from .routes.user_routes import user
    from .routes.term_routes import term
    from .routes.user_term_routes import user_term
    from .routes.verify_routes import verify

    app.register_blueprint(user, url_prefix='/users')
    app.register_blueprint(term, url_prefix='/terms')
    app.register_blueprint(user_term, url_prefix='/user_terms')
    app.register_blueprint(verify, url_prefix='/verify')

    return app