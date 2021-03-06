#-*- coding: utf-8 -*-
import subgetcore, os

####
PluginInfo = {'Requirements' : { 'OS' : 'Unix, Linux'}, 'API': 2, 'Authors': 'webnull', 'domain': '', 'type': 'extension', 'isPlugin': False, 'Description': 'zenity, kdialog and xmessage support to show error messages'}

class PluginMain(subgetcore.SubgetPlugin):
    """ Implements kdialog, xmessage, zenity to show error messages """

    subgetIcon = ""
    dialogCommand = None
    dialogType = "kdialog"
    errTypes = {}


    def _onErrorMessage(self, Data):
        self.sendEvent(str(Data[1]), str(Data[0])) # errType, message
        return Data

    def sendEvent(self, errType, Data):
        if errType == "info":
            errType = "msgbox"
        else:
            errType = "sorry"

        if self.dialogCommand == None:
            self.Subget.Logging.output("dialog disabled", "debug", False)
            return False

        # error type (zenity, xmessage and kdialog has diffirent types, so we need to translate them)
        errType = self.errTypes[self.dialogType][errType]

        # send a command to operating system
        command = self.dialogCommand.replace("{errType}", errType).replace("{Data}", Data).replace("{Icon}", self.subgetIcon).replace("{Title}", "Subget")


        self.Subget.Logging.output(command, "debug", False)
        os.system(command)

    def _pluginInit(self):
        """ Initialize plugin """
        self.subgetIcon = self.Subget.getPath("/usr/share/subget/icons/Subget-logo.xpm")
        self.Subget.Hooking.connectHook("onErrorMessage", self._onErrorMessage)
        forceConfigSetting = self.Subget.configGetKey("dialog", "type")

        if forceConfigSetting == "zenity":
            self.selectZenity()
            return True

        elif forceConfigSetting == "kdialog":
            self.selectKdialog()
            return True

        elif forceConfigSetting == "xmessage":
            self.selectXmessage()
            return True

        # Python 2.6 compatibility
        t = list()
        t.append('/usr/bin/zenity')
        t.append('/usr/local/bin/zenity')

        if self.Subget.getFile(t):
            self.selectZenity()
            return True

        t = list()
        t.append('/usr/bin/kdialog')
        t.append('/usr/local/bin/kdialog')

        if self.Subget.getFile(t):
            self.selectKdialog()
            return True


        t = list()
        t.append('/usr/bin/xmessage')
        t.append('/usr/local/bin/xmessage')

        if self.Subget.getFile({"/usr/bin/xmessage", "/usr/local/bin/xmessage"}):
            self.selectXmessage()
            return True

    def selectZenity(self):
        self.dialogCommand = "zenity --info --text=\"{Data}\" --title=\"{Title}\""
        self.dialogType = "zenity"
        self.errTypes['zenity'] = {'msgbox': 'info', 'sorry': 'error'}

    def selectKdialog(self):
        self.dialogCommand = "kdialog --{errType} \"{Data}\" --icon \"{Icon}\" --title \"{Title}\""
        self.dialogType = "kdialog"
        self.errTypes['kdialog'] = {'msgbox': 'msgbox', 'sorry': 'sorry'}

    def selectXmessage(self):
        self.dialogCommand = "xmessage \"{Data}\" -center"
        self.dialogType = "xmessage"
        self.errTypes['xmessage'] = {'msgbox': 'msgbox', 'sorry': 'sorry'}

    def _pluginDestroy(self):
        """ Unload plugin """
        del self
