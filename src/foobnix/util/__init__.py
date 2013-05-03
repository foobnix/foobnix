# -*- coding: utf-8 -*-

import sys
import logging
import traceback
from gi.repository import GObject


def idle_task(task):

    def idle(*args):
        def safe_task(*args):
            try:
                task(*args)
            except Exception as e:
                logging.error("Idle task raise an error: %s" % str(e))
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
        return GObject.idle_add(safe_task, *args)
    return idle

def idle_task_priority(priority=GObject.PRIORITY_DEFAULT_IDLE):

    def wrapper(task):
        def idle(*args):
            def safe_task(*args):
                try:
                    task(*args)
                except Exception as e:
                    logging.error("Idle task raise an error: %s" % str(e))
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
            return GObject.idle_add(safe_task, priority=priority, *args)
        return idle
    return wrapper