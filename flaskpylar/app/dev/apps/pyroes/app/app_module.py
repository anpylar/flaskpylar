###############################################################################
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
# Copyright 2018 Daniel Rodriguez. All Rights Reserved.
# Use of this source code is governed by the MIT license
###############################################################################
from anpylar import Module

from .app_component import AppComponent
from libs.api import ApiService


class AppModule(Module):
    services = {
        'api_service': ApiService,
    }

    routes = [
        {
            'path': '',
            'component': AppComponent,
        },
        {
            'path': '*',
            'redirect_to': '/',
        },
    ]
