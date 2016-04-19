#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Budy
# Copyright (c) 2008-2016 Hive Solutions Lda.
#
# This file is part of Hive Budy.
#
# Hive Budy is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Budy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Budy. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import time
import threading
import traceback

import appier

SLEEP_TIME = 1.0
""" The default sleep time to be used by the bots
in case no sleep time is defined in the constructor """

class Bot(threading.Thread):

    GLOBAL_LOCK = threading.RLock()

    def __init__(self, sleep_time = SLEEP_TIME, name = None, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.sleep_time = sleep_time
        self.name = name or self.__class__.__name__
        self.daemon = True

    def run(self):
        self.active = True

        while self.active:
            Bot.GLOBAL_LOCK.acquire()
            logger = appier.get_logger()
            logger.debug(
                "Tick operation started in %s" % self.name
            )
            try: self.tick()
            except BaseException as exception:
                lines = traceback.format_exc().splitlines()
                logger.debug(
                    "Failed tick due to %s (%s) in %s" %
                    (
                         str(exception),
                         exception.__class__.__name__,
                         self.name
                    ),
                    lines = lines
                )
            finally: Bot.GLOBAL_LOCK.release()
            logger.debug("Tick operation ended in %s" % self.name)
            logger.debug(
                "Sleeping for %d seconds in %s" %
                (self.sleep_time, self.name)
            )
            time.sleep(self.sleep_time)

    def stop(self):
        self.active = False

    def tick(self):
        raise appier.NotImplementedError()
