# encoding: utf-8

import os

from pysteam import paths as steam_paths
from pysteam import shortcuts
from pysteam import steam as steam_module

from ice import backups
from ice import configuration
from ice import consoles
from ice import emulators
from ice import paths
from ice import settings
from ice.logs import logger
from ice.persistence.config_file_backing_store import ConfigFileBackingStore

class TaskEngine(object):

  def __init__(self, steam):   
    self.steam = steam
    if not self.steam:
        if os.path.exists(steam_paths.default_linux_userdata_path()):
            self.steam = steam_module.Steam(steam_paths.default_linux_userdata_path())
        elif os.path.exists(steam_paths.default_osx_userdata_path()):
            self.steam = steam_module.Steam(steam_paths.default_osx_userdata_path())
        else:
            #### need to read config.txt to see the user custom setting
            if os.path.exists('config.txt'):
                for line in open('config.txt','r'):
                    if line[:8] == "Userdata":
                        # expand home alias
                        custom_path = line.split('=')[1].strip()
                        if custom_path[0] == '~':
                            custom_path = os.path.expanduser(custom_path)
                        else:
                            pass
                        
                        if os.path.exists(custom_path):
                            self.steam = steam_module.Steam(custom_path)
                        else:
                            logger.error('Path %s doesn\'t exist' % custom_path)
                    else:
                        pass
            else:
                logger.error("Can't find config.txt in current dir")
                return
    else:
        pass

    logger.debug("Initializing Ice")
    # We want to ignore the anonymous context, cause theres no reason to sync
    # ROMs for it since you cant log in as said user.
    is_user_context = lambda context: context.user_id != 'anonymous'
    self.users = None
    try:
        self.users = filter(is_user_context, steam_module.local_user_contexts(self.steam))
    except:
        logger.error("Failed to obtain user context")

  def run(self, tasks, app_settings, dry_run=False):
    if self.steam is None:
      logger.error("Cannot run Ice because Steam doesn't appear to be installed")
      return

    logger.info("=========== Starting Ice ===========")

    if self.users:
        for task in tasks:
          task(app_settings, self.users, dry_run=dry_run)
    else:
        logger.error("Couldn't tag users")
        return
