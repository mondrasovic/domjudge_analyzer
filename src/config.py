#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Milan Ondrašovič <milan.ondrasovic@gmail.com>

import abc


class Config(abc.ABC):
    """
    Common configurations.
    """


class DevelopmentConfig(Config):
    """
    Development configurations.
    """

    DEBUG = True


class ProductionConfig(Config):
    """
    Production configurations.
    """

    DEBUG = False


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
