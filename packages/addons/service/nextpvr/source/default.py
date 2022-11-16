# SPDX-License-Identifier: GPL-2.0-only
# Copyright (C) 2016-2022 Team LibreELEC (https://libreelec.tv)

import xbmc
import xbmcaddon

class Monitor(xbmc.Monitor):

   def __init__(self, *args, **kwargs):
      xbmc.Monitor.__init__(self)

   def onSettingsChanged(self):
      pass

if __name__ == "__main__":
   Monitor().waitForAbort()
