from flask import Flask, jsonify
from flask_smorest import Api
from db import db
from blocklist import BLOCKLIST
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate   
import os
import typing_extensions
import secrets
from urls.item import blp as ItemBlueprint
from urls.store import blp as StoreBlueprint
from urls.tag import blp as TagBlueprint
from urls.user import blp as UserBlueprint

def create_app(db_url=None):
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger.ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL","sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    migrate = Migrate(app, db)

    api = Api(app)

    # jwt extension
    app.config["JWT_SECRET_KEY"] = "Carlos" # secrets.SystemRandom().getrandbits(128)
    jwt = JWTManager(app)
    
    # blocklist
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    # Error message caused for the blocklist
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ), 
            401,
        )
    
    # ???
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required"
                }
            ),
            401
        )
    
    # claims
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity): 
        # Not the best practice, you should look in the database and see if the user is a admin
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    
    # Modify error messages
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"message": "The token has expired.", "error": "token_expired"}
            ),
            401
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401
        )    
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required"
                }
            ),
            401
        )
# We are using flask_Migrate, we dont need this any more
    # with app.app_context():
    #     db.create_all()

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app

# jwt required = Header > Authorization Bearer acces_token