from flask import Flask
from config import Config

### Remove for production
debug_config = True

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=debug_config)
