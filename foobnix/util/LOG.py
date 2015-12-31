'''
Created on Feb 26, 2010

@author: ivan
'''

import logging
with_print = False

levels = {
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "none": logging.CRITICAL,
    "debug": logging.DEBUG
}

def fprint(msg):
    if with_print:
        print msg
    else:
        logging.info(msg)

def setup(level="error", filename=None):
    log_level = level
    """
    Sets up the basic logger and if `:param:filename` is set, then it will log
    to that file instead of stdout.

    :param level: str, the level to log
    :param filename: str, the file to log to
    """
    if not level or level not in levels:
        level = "error"

    logging.getLogger("foobnix")
    logging.basicConfig(
        level=levels[level],
        format="[%(levelname)-8s] [%(asctime)s] [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%H:%M:%S",
        filename=filename,
        filemode="w"
    )

def print_platform_info():
    import platform
    logging.debug('*************** PLATFORM INFORMATION ************************')
    
    logging.debug('==Interpreter==')
    logging.debug('Version      :' + platform.python_version())
    logging.debug('Version tuple:' + str(platform.python_version_tuple()))
    logging.debug('Compiler     :' + platform.python_compiler())
    logging.debug('Build        :' + str(platform.python_build()))
    
    logging.debug('==Platform==')
    logging.debug('Normal :' + platform.platform())
    logging.debug('Aliased:' + platform.platform(aliased=True))
    logging.debug('Terse  :' + platform.platform(terse=True))
    
    logging.debug('==Operating System and Hardware Info==')
    logging.debug('uname:' + str(platform.uname()))
    logging.debug('system   :' + platform.system())
    logging.debug('node     :' + platform.node())
    logging.debug('release  :' + platform.release())
    logging.debug('version  :' + platform.version())
    logging.debug('machine  :' + platform.machine())
    logging.debug('processor:' + platform.processor())
    
    logging.debug('==Executable Architecture==')
    logging.debug('interpreter:' + str(platform.architecture()))
    logging.debug('/bin/ls    :' + str(platform.architecture('/bin/ls')))
    logging.debug('*******************************************************')

if __name__ == '__main__':
    setup("debug")
    print_platform_info()     
