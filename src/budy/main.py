#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

class BudyApp(appier.APIApp):

    def __init__(self):
        appier.APIApp.__init__(self, name = "budy")

if __name__ == "__main__":
    app = BudyApp()
    app.serve()
