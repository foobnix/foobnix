'''
Created on Feb 26, 2010

@author: ivan
'''

import logging

levels = {
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "none": logging.CRITICAL,
    "debug": logging.DEBUG
}

def setupLogger(level="error", filename=None):
    """
    Sets up the basic logger and if `:param:filename` is set, then it will log
    to that file instead of stdout.

    :param level: str, the level to log
    :param filename: str, the file to log to
    """

    if not level or level not in levels:
        level = "error"

    logging.basicConfig(
        level=levels[level],
        format="[%(levelname)-8s] %(asctime)s %(module)s:%(lineno)d %(message)s",
        datefmt="%H:%M:%S",
        filename=filename,
        filemode="w"
    )

def set_logger_level(level):
    if level not in levels:
        return
    
    logging.getLogger("foobnix")
    logging.basicConfig(level=levels[level])

debug = lambda * a: logging.debug(a)
info = lambda * a: logging.info(a)
warning = lambda * a: logging.warning(a)
warn = lambda * a: logging.warning(a)
error = lambda * a: logging.error(a)
critical = lambda * a: logging.critical(a)



def print_platform_info():
    import platform
    debug('*************** PLATFORM INFORMATION ************************')
    
    debug('==Interpreter==')
    debug('Version      :', platform.python_version())
    debug('Version tuple:', platform.python_version_tuple())
    debug('Compiler     :', platform.python_compiler())
    debug('Build        :', platform.python_build())
    
    debug('==Platform==')
    debug('Normal :', platform.platform())
    debug('Aliased:', platform.platform(aliased=True))
    debug('Terse  :', platform.platform(terse=True))
    
    debug('==Operating System and Hardware Info==')
    debug('uname:', platform.uname())
    debug('system   :', platform.system())
    debug('node     :', platform.node())
    debug('release  :', platform.release())
    debug('version  :', platform.version())
    debug('machine  :', platform.machine())
    debug('processor:', platform.processor())
    
    debug('==Executable Architecture==')
    debug('interpreter:', platform.architecture())
    debug('/bin/ls    :', platform.architecture('/bin/ls'))
    debug('*******************************************************')
        
