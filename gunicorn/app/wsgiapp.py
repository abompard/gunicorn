# -*- coding: utf-8 -
#
# This file is part of gunicorn released under the MIT license.
# See the NOTICE for more information.

import os

from gunicorn.errors import ConfigError
from gunicorn.app.base import Application
from gunicorn import util


class WSGIApplication(Application):
    def init(self, parser, opts, args):
        if opts.paste:
            from .pasterapp import has_logging_config

            config_uri = os.path.abspath(opts.paste)
            config_file = config_uri.split('#')[0]

            if not os.path.exists(config_file):
                raise ConfigError("%r not found" % config_file)

            self.cfg.set("default_proc_name", config_file)
            self.app_uri = config_uri

            if has_logging_config(config_file):
                self.cfg.set("logconfig", config_file)

            return

        if args:
            self.app_uri = args[0]
        elif self.cfg.wsgi_app:
            self.app_uri = self.cfg.wsgi_app
        else:
            parser.error("No application module specified.")

        self.cfg.set("default_proc_name", self.app_uri)

    def load_wsgiapp(self):
        return util.import_app(self.app_uri)

    def load_pasteapp(self):
        from .pasterapp import get_wsgi_app
        return get_wsgi_app(self.app_uri, defaults=self.cfg.paste_global_conf)

    def load(self):
        if self.cfg.paste is not None:
            return self.load_pasteapp()
        else:
            return self.load_wsgiapp()


def run():
    """\
    The ``gunicorn`` command line runner for launching Gunicorn with
    generic WSGI applications.
    """
    from gunicorn.app.wsgiapp import WSGIApplication
    WSGIApplication("%(prog)s [OPTIONS] [APP_MODULE]").run()


if __name__ == '__main__':
    run()
