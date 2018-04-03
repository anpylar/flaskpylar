###############################################################################
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
# Copyright 2018 Daniel Rodriguez. All Rights Reserved.
# Use of this source code is governed by the MIT license
###############################################################################
from anpylar import Component, window, call_delayed


class AppComponent(Component):
    bindings = {
        'user': '',
        'pwd': '',
        'auth_error_timeout': 2000.0,  # 2 secs
    }

    def render(self, node):
        username = node.select('input[name="username"]')
        username._fmtval(self.user_)

        password = node.select('input[name="password"]')
        password._fmtval(self.pwd_)

        btn = node.select('input[type="button"]')
        btn._bindx.click(self.login)

        self.footer = node.select('div[name="login-footer"]')
        self.footer._display_toggle(False)

    def login(self):
        def urldecode(s):
            duc = window.decodeURIComponent
            result = {}
            for kv in resp.text.split('&'):
                k, v = kv.split('=')
                result[duc(k)] = duc(v)

            return result

        def post_login(resp):
            if resp.status == 401:
                self.footer.set_html('Authentication failed!')
                self.footer._display_toggle(True)

                def kill_footer():
                    self.footer._display_toggle(False)

                call_delayed(self.auth_error_timeout, kill_footer)
                return

            elif resp.status != 200:
                return

            result = urldecode(resp.text)
            next_to = result.pop('next', None)
            print('navigating to:', next_to, result)
            if next_to:
                self.router.navigate_to(next_to, **result)

        self.api_service.login(self.user, self.pwd).subscribe(post_login)
