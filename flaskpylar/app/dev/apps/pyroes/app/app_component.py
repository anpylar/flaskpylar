###############################################################################
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
# Copyright 2018 Daniel Rodriguez. All Rights Reserved.
# Use of this source code is governed by the MIT license
###############################################################################
from anpylar import ComponentInline, html as h

from libs.hello import hello


class AppComponent(ComponentInline):
    htmlsheet = '''
    <h2>Hello Pyroes</h2>
    <ul></ul>
    <button class="btn btn-lg btn-primary">Logout</button>
    '''

    bindings = {
        'pyroes': [],
    }

    def loading(self):
        self.api_service.get_pyroes().subscribe(self.pyroes_)

    def render(self, node):
        btn = node.select('button')
        btn._bindx.click(self.logout)

        def ul_pyroes(pyroes):
            print
            for p in pyroes:
                h.li('{pyd}: {name}'.format(**p))

        node.select('ul')._render(ul_pyroes, self.pyroes_)

        # Call also our hello method
        hello()

    def logout(self):
        def post_logout(r):
            self.router.navigate_to('/')  # safe choice after logout

        self.api_service.logout().subscribe(post_logout)
