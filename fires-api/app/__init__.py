from flask import Flask
from config import Config
from core import limiter

### Remove for production
debug_config = True

def create_app(config_class=Config):
    app = Flask(__name__)
    limiter.init_app(app)

    app.config.from_object(config_class)

    from app.api import bp as api_bp, set_limiter
    app.register_blueprint(api_bp, url_prefix='/api')
    set_limiter(app.config['REQUEST_LIMIT'])

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=debug_config)
