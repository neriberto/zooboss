from __future__ import absolute_import

import os
import sys
import zooboss

if __package__ == '':
  sys.path.insert(
      0,
      os.path.dirname(os.path.dirname(__file__)))

if __name__ == '__main__':
  sys.exit(zooboss.main())
