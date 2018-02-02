#!/usr/bin/env python
# encoding: utf-8
"""
retrogamingcloud_provider.py

Created by sairuk on 2018-02-??
CopyBlah (c) Blah Blah ... GPLv2
"""

import sys
import os
import urllib
import urllib2
import json

import grid_image_provider

from ice.logs import logger

class RetrogamingCloudGridProvider(grid_image_provider.GridImageProvider):

  @staticmethod
  def api_url():
    return "http://retrogaming.cloud/api/v1"

  @staticmethod
  def is_enabled():
    # TODO: Return True/False based on the current network status
    return True

  def retrogaming_cloud_media_url(self, romid, rom):
    host = self.api_url()
    return "%s/game/%s/media" % (host, romid)

  def retrogaming_cloud_game_id(self, rom):
      host = self.api_url()
      quoted_name = urllib.quote(rom.name)
      return "%s/platform/%s/game?name=%s" % (host, rom.console.shortname, quoted_name)

  def find_url_for_rom(self, url, rom):
    """
    Determines a suitable grid image for a given ROM by hitting
    retrogaming.cloud
    """
    try:
      response = urllib2.urlopen(url)
      return response
    except urllib2.URLError as error:
      # Connection was refused. retrogaming.cloud may be down, or something bad
      # may have happened
      logger.debug(
        "%s failed to an error with retrogaming.cloud" % url
      )

  def download_image(self, url):
    """
    Downloads the image at 'url' and returns the path to the image on the
    local filesystem
    """
    (path, headers) = urllib.urlretrieve(url)
    return path

  def image_for_rom(self, rom):
    game_id = None
    image_url = None
    game_url_json = self.find_url_for_rom(self.retrogaming_cloud_game_id(rom), rom)
    if game_url_json is not None and game_url_json.getcode() == 200:
        game_id = json.loads(game_url_json.read())['results'][0]['id']
        if game_id:
            image_url_json = self.find_url_for_rom(self.retrogaming_cloud_media_url(game_id,rom), rom)
            if image_url_json is not None and image_url_json.getcode() == 200:
                image_url = json.loads(image_url_json.read())['results'][0]['url']
                if image_url is None or image_url == "":
                  return None
                return self.download_image(image_url)
            else:
                return None
        else:
            return None
    else:
        return None
    
