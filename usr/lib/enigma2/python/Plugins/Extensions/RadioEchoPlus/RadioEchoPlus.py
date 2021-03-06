# -*- coding: utf-8 -*-
#
#  RadioEchoPlus Player
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

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Components.Label import Label
from enigma import eServiceReference, iServiceInformation, eTimer, ePicLoad
import time, os, json, urllib, urllib2, subprocess, requests
from Tools.Directories import fileExists
from shutil import move

coverpath = "/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/echoplus_RADIO.jpg"
songtitle = ''
screenchange = "waiting"

class RadioEchoPlus(Screen):
	skin = """
			<screen name="RadioEchoPlus" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="#ff000000">
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/bottom.png" position="0,640" size="1280,80" zPosition="-9" alphatest="blend" />
				<eLabel position="0,640" size="1280,2" backgroundColor="#000c0893" zPosition="-8" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/top.png" position="0,0" size="1280,59" zPosition="-9" alphatest="blend" />
				<eLabel position="0,58" size="1280,2" backgroundColor="#000c0893" zPosition="-8" />
				<widget backgroundColor="#00120f2d" source="Title" render="Label" font="Regular;34" foregroundColor="#00ffc000" position="42,7" size="736,46" valign="center" transparent="1" />
				<widget source="global.CurrentTime" render="Label" position="1138,16" size="100,28" font="Regular;26" halign="right" backgroundColor="#00120f2d" transparent="1" valign="center" foregroundColor="#00ffffff">
					<convert type="ClockToText">Default</convert>
				</widget>
				<eLabel backgroundColor="#00000000" text="Jetzt läuft:" font="Regular;30" foregroundColor="#00ffc000" position="42,70" size="609,38" halign="center" valign="center" transparent="1" />
				<widget backgroundColor="#00000000" source="songtitle" render="Label" font="Regular;30" foregroundColor="#00ffffff" position="42,120" size="609,76" halign="center" valign="top" transparent="1" />
				<widget backgroundColor="#00000000" name="cover" position="146,220" size="400,400" zPosition="1" />
				<widget backgroundColor="#00120f2d" source="key_red" render="Label" font="Regular;20" foregroundColor="#00ffffff" position="47,670" size="220,26" valign="center" transparent="1" zPosition="1" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/key_red.png" position="42,697" size="200,5" alphatest="blend" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/key_green.png" position="292,697" size="200,5" alphatest="blend" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/key_yellow.png" position="542,697" size="200,5" alphatest="blend" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/key_blue.png" position="792,697" size="200,5" alphatest="blend" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/key_exit.png" position="1195,675" size="43,22" alphatest="blend" />
				<eLabel backgroundColor="#00120f2d" text="echosat AUSTRIA" position="693,16" size="278,28" font="Regular;26" foregroundColor="#00ffc000" halign="left" valign="center" transparent="1" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/logo.png" position="693,76" size="545,180" alphatest="blend" />
				<eLabel backgroundColor="#00000000" text="mehr ECHO, mehr PLUS" position="693,320" size="545,35" font="Regular;28" foregroundColor="#00ffc000" halign="center" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" text="Genre: " position="781,390" size="150,30" font="Regular;24" foregroundColor="#00ffc000" halign="left" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" text=" 70er, 80er, 90er" position="950,390" size="200,30" font="Regular;24" foregroundColor="#00ffffff" halign="right" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" text="Land: " position="781,440" size="150,30" font="Regular;24" foregroundColor="#00ffc000" halign="left" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" text="Österreich" position="950,440" size="200,30" font="Regular;24" foregroundColor="#00ffffff" halign="right" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" text="Stadt: " position="781,490" size="150,30" font="Regular;24" foregroundColor="#00ffc000" halign="left" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" text=" Ansfelden" position="950,490" size="200,30" font="Regular;24" foregroundColor="#00ffffff" halign="right" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" text="echo-plus.at" position="693,555" size="545,35" font="Regular;28" foregroundColor="#00ffc000" halign="center" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" position="0,0" size="1280,720" transparent="0" zPosition="-10" />
			</screen>
			"""

	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		self.session = session
		self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		self.oldSongTitle = ''
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["cover"] = Pixmap()

		self["actions"] = ActionMap(["OkCancelActions","ColorActions"],
		{
			"red": self.exit,
			"cancel": self.exit
		}, -2)

		self["key_red"] = StaticText(_("Exit"))
		self["Title"] = StaticText("Radio ECHOPLUS")
		self["songtitle"] = StaticText()

		self.infotimer = eTimer()
		self.infotimer.callback.append(self.getInfos)
		self.covertimer = eTimer()
		self.abouttimer = eTimer()
		self.abouttimer.callback.append(self.showAbout)
		self.InternetAvailable = self.getInternetAvailable()
		self.play()
		self.updatePicture()

	def play(self):
		try:
			if self.InternetAvailable:
				self.session.nav.stopService()
				URL = "4097:0:0:0:0:0:0:0:0:0:http%3a//radio2.stream24.net%3a9120/live.mp3"
				stream = eServiceReference(URL)
				self.session.nav.playService(stream)
				self.infotimer.start(2000, True)
			else:
				self.close()
		except:
			self.close()

	def getInfos(self):
		self.infotimer.stop()
		self.startAboutSwitchTimer()
		self.getSongTitle()
		self.changeSongTitle()
		self.checkNewSongTitle()
		self.infotimer.start(2000, True)

	def startAboutSwitchTimer(self):
		global screenchange
		if screenchange == "waiting":
			screenchange = "running"
			self.abouttimer.start(15000, True)

	def getSongTitle(self):
		global songtitle
		url = "http://radio2.stream24.net:9120/live.mp3"
		request = urllib2.Request(url)
		try:
			request.add_header("Icy-MetaData", 1)
			response = urllib2.urlopen(request)
			icy_metaint_header = response.headers.get("icy-metaint")
			if icy_metaint_header is not None:
				metaint = int(icy_metaint_header)
				read_buffer = metaint + 255
				content = response.read(read_buffer)
				title = content[metaint:].replace("StreamTitle='", "MetaDataTitle").replace("';", "MetaDataTitle").decode("latin-1").encode("utf-8")
				songtitle = str(title.split("MetaDataTitle")[1])
			else:
				songtitle = "Radio ECHOPLUS - kein Songtitel gefunden"
		except:
			songtitle = "Radio ECHOPLUS - kein Songtitel gefunden"

	def changeSongTitle(self):
		global songtitle
		if songtitle == " - WERBUNG":
			songtitle = "Radio ECHOPLUS - Werbung"
		if songtitle in (" - Radio ECHOPLUS"," - Radio ECHOPLUS2"," - Radio ECHOPLUS3"," - www.Radio Echoplus"):
			songtitle = "Radio ECHOPLUS - Info"
		if songtitle == " - 70igerECHOPLUS":
			songtitle = "Radio ECHOPLUS - 70iger"
		if songtitle == " - OLDIES":
			songtitle = "Radio ECHOPLUS - Oldies"
		if songtitle == " - NACHRICHTEN":
			songtitle = "Radio ECHOPLUS - Nachrichten"

	def checkNewSongTitle(self):
		global songtitle
		if songtitle != self.oldSongTitle:
			print "RadioEchoPlus: playing ... " + songtitle
			self["songtitle"].setText(songtitle)
			self.getCover()

	def getCover(self):
		global songtitle, coverpath
		if songtitle == "Radio ECHOPLUS - kein Songtitel gefunden":
			coverpath = "/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/echoplus_RADIO.jpg"
		elif songtitle == "Radio ECHOPLUS - Werbung":
			coverpath = "/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/Werbung.jpg"
		elif songtitle == "Radio ECHOPLUS - Info":
			coverpath = "/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/Info.jpg"
		elif songtitle == "Radio ECHOPLUS - 70iger":
			coverpath = "/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/70iger.jpg"
		elif songtitle == "Radio ECHOPLUS - Oldies":
			coverpath = "/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/Oldies.jpg"
		elif songtitle == "Radio ECHOPLUS - Nachrichten":
			coverpath = "/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/Nachrichten.jpg"
		else:
			try:
				self.downloadCover("450x450")
				if os.path.getsize("/tmp/echoplus_cover.jpg") == 0:
					self.tryDownloadAgain()
				else:
					coverpath = "/tmp/echoplus_cover.jpg"
			except:
				self.tryDownloadAgain()
		self.covertimer.start(200, True)
		self.oldSongTitle = songtitle

	def tryDownloadAgain(self):
		global coverpath
		try:
			self.downloadCover("300x300")
			if os.path.getsize("/tmp/echoplus_cover.jpg") == 0:
				coverpath = "/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/echoplus_RADIO.jpg"
			else:
				coverpath = "/tmp/echoplus_cover.jpg"
		except:
			coverpath = "/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/echoplus_RADIO.jpg"

	def downloadCover(self, resolution):
		global songtitle
		res = requests.get("http://itunes.apple.com/search?term=%s&limit=1&media=music" % (urllib.quote_plus(songtitle)), timeout=1)
		data = res.json()
		url = data['results'][0]['artworkUrl100'].encode('utf-8')
		url = url.replace("100x100", resolution).replace('https', 'http')
		sub = subprocess.Popen("wget -q " + url + " -O /tmp/echoplus_cover.jpg", shell = True)
		sub.wait()

	def updatePicture(self):
		self.PicLoad.PictureData.get().append(self.decodePicture)
		self.covertimer.callback.append(self.showPicture)

	def showPicture(self):
		global coverpath
		self.PicLoad.setPara([self["cover"].instance.size().width(),self["cover"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#00000000"])
		self.PicLoad.startDecode(coverpath)
		self.covertimer.stop()

	def decodePicture(self, PicInfo = ""):
		ptr = self.PicLoad.getData()
		self["cover"].instance.setPixmap(ptr)

	def showAbout(self):
		self.abouttimer.stop()
		self.session.open(RadioEchoPlusAbout)

	def exit(self):
		global screenchange
		screenchange = ""
		if self.abouttimer.isActive():
			self.abouttimer.stop()
		askExit = self.session.openWithCallback(self.doExit,MessageBox,_("Do you really want to exit?"), MessageBox.TYPE_YESNO)
		askExit.setTitle(_("Exit"))

	def doExit(self,answer):
		if answer is True:
			if self.covertimer.isActive():
				self.covertimer.stop()
			if self.infotimer.isActive():
				self.infotimer.stop()
			self.session.nav.stopService()
			self.session.nav.playService(self.oldService)
			self.close()
		else:
			global screenchange
			screenchange = "waiting"
			pass

	def getInternetAvailable(self):
		import ping
		r = ping.doOne("8.8.8.8",1.5)
		if r != None and r <= 1.5:
			return True
		else:
			return False

class RadioEchoPlusAbout(Screen):
	skin = """
			<screen name="RadioEchoPlusAbout" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="#ff002b57">
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/bottom.png" position="0,640" size="1280,80" zPosition="-9" alphatest="blend" />
				<eLabel position="0,640" size="1280,2" backgroundColor="#000c0893" zPosition="-8" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/top.png" position="0,0" size="1280,59" zPosition="-9" alphatest="blend" />
				<eLabel position="0,58" size="1280,2" backgroundColor="#000c0893" zPosition="-8" />
				<widget backgroundColor="#00120f2d" source="Title" render="Label" font="Regular;34" foregroundColor="#00ffc000" position="42,7" size="736,46" valign="center" transparent="1" />
				<widget source="global.CurrentTime" render="Label" position="1138,16" size="100,28" font="Regular;26" halign="right" backgroundColor="#00120f2d" transparent="1" valign="center" foregroundColor="#00ffffff">
					<convert type="ClockToText">Default</convert>
				</widget>
				<eLabel backgroundColor="#00000000" text="Unser Studio:" font="Regular;27" position="42,80" size="609,34" foregroundColor="#00ffc000" transparent="1" />
				<eLabel backgroundColor="#00000000" text="Satellitenplatz 1" font="Regular;24" position="54,125" size="597,30" foregroundColor="#00ffffff" transparent="1" />
				<eLabel backgroundColor="#00000000" text="4052 Ansfelden" font="Regular;24" position="54,155" size="597,30" foregroundColor="#00ffffff" transparent="1" />
				<eLabel backgroundColor="#00000000" text="Kontakt:" font="Regular;27" position="42,225" size="609,34" foregroundColor="#00ffc000" transparent="1" />
				<eLabel backgroundColor="#00000000" text="Studiotelefon: 0043 676 9191408" font="Regular;24" position="54,270" size="597,30" foregroundColor="#00ffffff" transparent="1" />
				<eLabel backgroundColor="#00000000" text="e-mail: office@echo-plus.at" font="Regular;24" position="54,300" size="597,30" foregroundColor="#00ffffff" transparent="1" />
				<eLabel backgroundColor="#00000000" text="Stream:" font="Regular;27" position="42,370" size="609,34" foregroundColor="#00ffc000" transparent="1" />
				<eLabel backgroundColor="#00000000" text="Radio ECHOPLUS Livestream von stream24.de" font="Regular;24" position="54,415" size="597,30" foregroundColor="#00ffffff" transparent="1" />
				<eLabel backgroundColor="#00000000" text="Jetzt läuft:" font="Regular;27" position="42,485" size="609,34" foregroundColor="#00ffc000" transparent="1" />
				<widget backgroundColor="#00000000" source="songtitle" render="Label" font="Regular;24" position="54,530" size="597,60" foregroundColor="#00ffffff" valign="top" transparent="1" />
				<widget backgroundColor="#00120f2d" source="key_red" render="Label" font="Regular;20" foregroundColor="#00ffffff" position="47,670" size="220,26" valign="center" transparent="1" zPosition="1" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/key_red.png" position="42,697" size="200,5" alphatest="blend" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/key_green.png" position="292,697" size="200,5" alphatest="blend" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/key_yellow.png" position="542,697" size="200,5" alphatest="blend" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/key_blue.png" position="792,697" size="200,5" alphatest="blend" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/key_exit.png" position="1195,675" size="43,22" alphatest="blend" />
				<eLabel backgroundColor="#00120f2d" text="echosat AUSTRIA" position="693,16" size="278,28" font="Regular;26" foregroundColor="#00ffc000" halign="left" valign="center" transparent="1" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RadioEchoPlus/graphics/logo.png" position="693,76" size="545,180" alphatest="blend" />
				<eLabel backgroundColor="#00000000" text="mehr ECHO, mehr PLUS" position="693,320" size="545,35" font="Regular;28" foregroundColor="#00ffc000" halign="center" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" text="Genre: " position="781,390" size="150,30" font="Regular;24" foregroundColor="#00ffc000" halign="left" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" text=" 70er, 80er, 90er" position="950,390" size="200,30" font="Regular;24" foregroundColor="#00ffffff" halign="right" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" text="Land: " position="781,440" size="150,30" font="Regular;24" foregroundColor="#00ffc000" halign="left" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" text="Österreich" position="950,440" size="200,30" font="Regular;24" foregroundColor="#00ffffff" halign="right" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" text="Stadt: " position="781,490" size="150,30" font="Regular;24" foregroundColor="#00ffc000" halign="left" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" text=" Ansfelden" position="950,490" size="200,30" font="Regular;24" foregroundColor="#00ffffff" halign="right" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" text="echo-plus.at" position="693,555" size="545,35" font="Regular;28" foregroundColor="#00ffc000" halign="center" valign="center" transparent="1" />
				<eLabel backgroundColor="#00000000" position="0,0" size="1280,720" transparent="0" zPosition="-10" />
			</screen>
			"""

	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		self.session = session
		self.oldSongTitle = ''

		self["actions"] = ActionMap(["OkCancelActions","ColorActions"],
		{
			"red": self.hideAbout,
			"cancel": self.hideAbout
		}, -2)

		self["key_red"] = StaticText(_("Back"))
		self["Title"] = StaticText("Über Radio ECHOPLUS")
		self["songtitle"] = StaticText()

		self.exittimer = eTimer()
		self.exittimer.callback.append(self.hideAbout)
		self.infotimer = eTimer()
		self.infotimer.callback.append(self.getSongTitle)
		self.onLayoutFinish.append(self.getSongTitle)

	def getSongTitle(self):
		self.infotimer.start(1000, True)
		global songtitle, screenchange
		if screenchange == "running":
			screenchange = ""
			self.exittimer.start(15000, True)
		if songtitle != self.oldSongTitle:
			self["songtitle"].setText(songtitle)
			self.oldSongTitle = songtitle

	def hideAbout(self):
		global screenchange
		screenchange = "waiting"
		self.exittimer.stop()
		self.infotimer.stop()
		self.close()
