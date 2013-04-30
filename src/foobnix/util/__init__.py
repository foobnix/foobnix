# -*- coding: utf-8 -*-

import logging
from gi.repository import GObject


def idle_task(task):

    def idle(*args):
        def safe_task(*args):
            try:
                task(*args)
            except Exception as e:
                logging.error("Idle task raise an error: %s" % str(e))
        return GObject.idle_add(safe_task, *args)
    return idle