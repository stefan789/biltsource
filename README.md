biltsource
==========

class Bilt to control all Bilt sources, configuration is read from file sources.dict


make sure the source you want to use is listed in sources.dict

using the soure atm:
use source 37(?)

example:

import biltsource as b
b37=b.BiltSource(37)
b37.setvoltage(1.2)
b37.on()

