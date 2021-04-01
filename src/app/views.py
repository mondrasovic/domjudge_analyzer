#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Milan Ondrašovič <milan.ondrasovic@gmail.com>

from flask import render_template

from app import app


@app.route('/')
def homepage():
    """
    Render the homepage template on the / route.
    """
    return render_template('index.html')
