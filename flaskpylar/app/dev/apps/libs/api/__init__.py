###############################################################################
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
# Copyright 2018 Daniel Rodriguez. All Rights Reserved.
# Use of this source code is governed by the MIT license
###############################################################################
from anpylar import http, Service

import json


class ApiService(Service):
    token = ''

    def __init__(self):
        self.http = http.Http(
            url='/api',
            fullresp=True,  # not only body, but full response, incl status
        )

    def login(self, username, password):
        data = {'username': username, 'password': password}
        # Be Specific about encoding of body
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return self.http.post(url='login', headers=headers, data=data)

    def logout(self):
        return self.http.get(url='logout')

    def get_pyroes(self):
        def pyroes_decode(resp):
            pyroes = []
            if resp.status == 200:
                try:
                    pyroes = json.loads(resp.text)
                except:
                    pass

            return pyroes

        return self.http.get(url='pyroes').map(pyroes_decode)
