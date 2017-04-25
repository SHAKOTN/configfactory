from gunicorn.app.base import BaseApplication


class ServerApplication(BaseApplication):

    def __init__(self, wsgi_app, options=None):
        self.options = options or {}
        self.wsgi_app = wsgi_app
        super().__init__()

    def init(self, parser, opts, args):
        pass

    def load_config(self):
        config = dict(
            [
                (key, value)
                for key, value in self.options.items()
                if key in self.cfg.settings and value is not None
            ]
        )
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.wsgi_app
