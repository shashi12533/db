from db import create_app
from db.api.views import api as api_module
# FIXME: naming has to be symmetric - why not 'db.custom_api.views'?
from db.custom_api.custom_api_blueprint import custom_api_bp as custom_api_module


if __name__ == '__main__':
    app = create_app('config.ProductionConfig')
    app.register_blueprint(api_module)
    app.register_blueprint(custom_api_module)
    app.run(host="0.0.0.0", port=int(app.config['PORT']))
