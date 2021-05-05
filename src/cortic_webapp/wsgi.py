""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, November 2019

"""

import sys
sys.path.insert(0, '/home/pi/CAIT_CURT/cait/src')

from main import application 

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=80, threaded=True)