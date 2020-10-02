# -*- coding: utf-8 -*-
#
#  Plugin Code
#
#  Coded/Modified/Adapted by örlgrey
#  Based on teamBlue image source code
#
#  This code is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ 
#  or send a letter to Creative Commons, 559 Nathan 
#  Abbott Way, Stanford, California 94305, USA.
#
#  If you think this license infringes any rights,
#  please contact me at ochzoetna@gmail.com

from Plugins.Plugin import PluginDescriptor
import RadioEchoPlus

def main(session, **kwargs):
	reload(RadioEchoPlus)
	try:
		session.open(RadioEchoPlus.RadioEchoPlus)
	except:
		import traceback
		traceback.print_exc()

def Plugins(**kwargs):
	list = []
	list.append(PluginDescriptor(name="RadioEchoPlus", description=_("RadioEchoPlus-Player"), where = PluginDescriptor.WHERE_PLUGINMENU, icon='plugin.png', fnc=main))
	return list
