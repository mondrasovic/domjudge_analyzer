#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Milan Ondrašovič <milan.ondrasovic@gmail.com>

from flask import Flask

from config import app_config


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])

    return app


app = create_app('development')
