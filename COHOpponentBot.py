VersionNumber = "Version 1.0"

import IRCBetBot_Parameters
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import re
import os.path
import COHOpponentBot_1
import threading
from queue import Queue # to talk to the threads
from tkinter import *
from tkinter.ttk import *
from tkinter import ttk
import base64
import os

import logging # For logging information and warnings about opperation errors


class COHBotGUI:

    def __init__(self):

        self.thread = None #reference to the opponentbot



        self.parameters = IRCBetBot_Parameters.parameters()
        self.parameters.load()

        self.master = tk.Tk()

        self.optionsMenu = None

        self.style = Style()
        self.master.title("COH Opponent Bot")

        #checkbox string construction option bools

        self.showOwn = IntVar(value = int(bool(self.parameters.data.get('showOwn'))))

        self.automaticMode = IntVar(value = int(bool(self.parameters.data.get('automaticMode'))))
        
        self.showBasic = IntVar(value = int(bool(self.parameters.data.get('showBasic'))))
        self.show1v1 = IntVar(value = int(bool(self.parameters.data.get('show1v1'))))
        self.show2v2 = IntVar(value = int(bool(self.parameters.data.get('show2v2'))))
        self.show3v3 = IntVar(value = int(bool(self.parameters.data.get('show3v3'))))
        
        self.showWins = IntVar(value = int(bool(self.parameters.data.get('showWins'))))
        self.showLosses = IntVar(value = int(bool(self.parameters.data.get('showLosses'))))
        self.showDisputes = IntVar(value = int(bool(self.parameters.data.get('showDisputes'))))
        self.showStreak = IntVar(value = int(bool(self.parameters.data.get('showStreak'))))
        self.showDrops = IntVar(value = int(bool(self.parameters.data.get('showDrops'))))
        self.showRank = IntVar(value = int(bool(self.parameters.data.get('showRank'))))
        self.showLevel = IntVar(value = int(bool(self.parameters.data.get('showLevel'))))
        self.showLastPlayed = IntVar(value = int(bool(self.parameters.data.get('showLastPlayed'))))
        
        self.showWLRatio = IntVar(value = int(bool(self.parameters.data.get('showWLRatio'))))

        self.showSteamProfile = IntVar(value = int(bool(self.parameters.data.get('showSteamProfile'))))
        self.showUserCountry = IntVar(value = int(bool(self.parameters.data.get('showUserCountry'))))

        self.automaticTrigger = IntVar(value = int(bool(self.parameters.data.get('automaticTrigger'))))

        tk.Label(self.master, text="Twitch Channel").grid(row=0, sticky=tk.W)
        tk.Label(self.master, text="Bot Account Name").grid(row=1, sticky=tk.W)
        tk.Label(self.master, text="Bot oAuth Key").grid(row=2, sticky=tk.W)
        tk.Label(self.master, text="Steam64ID Number").grid(row=3, sticky=tk.W)
        tk.Label(self.master, text="warning.log path").grid(row=4, sticky=tk.W)

        self.e1 = tk.Entry(self.master, width = 70)
        self.e2 = tk.Entry(self.master, width = 70)
        self.e3 = tk.Entry(self.master, width = 70)
        self.e4 = tk.Entry(self.master, width = 70)
        self.e5 = tk.Entry(self.master, width = 70)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        self.e4.grid(row=3, column=1)
        self.e5.grid(row=4, column=1)

        logPath = self.parameters.data.get('logPath')
        if (logPath):
            self.e5.insert(0, str(logPath))

        steamNumber = "enter your steam number"
        if self.parameters.data.get('steamNumber'):
            steamNumber = self.parameters.data.get('steamNumber')

        self.e4.insert(0, steamNumber)

        twitchName = "enter your twitch channel name"
        if self.parameters.data.get('channel'):
            twitchName = self.parameters.data.get('channel')

        self.e1.insert(0, twitchName)
        if (self.parameters.data.get('botUserName')):
            self.e2.insert(0, str(self.parameters.data.get('botUserName')))

        if (self.parameters.data.get('botOAuthKey')):
            self.e3.insert(0, str(self.parameters.data.get('botOAuthKey')))

        self.e1.config(state = "disabled")
        self.e2.config(state = "disabled")
        self.e3.config(state = "disabled")
        self.e4.config(state = "disabled")
        self.e5.config(state = "disabled")

        self.b1 = tk.Button(self.master, text = "edit", command = lambda: self.editTwitchName())
        self.b1.config(width = 10)
        self.b1.grid(row=0, column =2)
        self.b2 = tk.Button(self.master, text = "edit", command = lambda: self.editBotName())
        self.b2.config(width = 10)
        self.b2.grid(row=1, column=2)
        self.b3 = tk.Button(self.master, text = "edit", command = lambda: self.editOAuthKey())
        self.b3.config(width = 10)
        self.b3.grid(row=2, column=2)
        self.b4 = tk.Button(self.master, text = "edit", command = lambda: self.editSteamNumber())
        self.b4.config(width = 10)
        self.b4.grid(row=3, column=2)        
        self.b5 = tk.Button(self.master, text = "browse", command = lambda : self.locateWarningLog() )
        self.b5.config(width = 10)
        self.b5.grid(row=4, column=2)
        self.b6 = tk.Button(self.master, text = "options", command = self.createOptionsMenu )
        self.b6.config(width = 10)
        self.b6.grid(row=5, column=2)



        self.thread = None
        self.automaticFileMonitor = None

        self.style.configure('W.TButton', font = 'calibri', size = 10, foreground = 'red')
        self.connectButton = ttk.Button(self.master, text = "Connect",style ='W.TButton', command = lambda : self.connectIRC(self.thread))
        #self.connectButton.config(width = 10, height = 5)
        self.connectButton.grid(row=6, columnspan = 3, sticky = tk.W+tk.E+tk.N+tk.S, padx=30,pady=30)

        #self.master.iconbitmap('coh.ico')
        self.consoleDisplayBool = IntVar()
        checkButton1 = tk.Checkbutton(self.master, text="Display IRC raw chat output", variable=self.consoleDisplayBool, command = self.displayConsoleToggled)
        checkButton1.grid(row=8, sticky=tk.W)

        self.testButton = tk.Button(self.master, text = "Test Output", command = self.testStats )
        self.testButton.config(width = 10)
        self.testButton.grid(row =8, column=2 ,sticky=tk.E)
        self.testButton.config(state = DISABLED)


        tk.Label(self.master, text="Console Output:").grid(row=9, sticky=tk.W)
        # create a Text widget
        self.txt = tk.Text(self.master)
        self.txt.grid(row=10, columnspan=3, sticky="nsew", padx=2, pady=2)

        # create a Scrollbar and associate it with txt
        scrollb = ttk.Scrollbar(self.master, command=self.txt.yview)
        scrollb.grid(row=8, column=4, sticky='nsew')
        self.txt['yscrollcommand'] = scrollb.set


        # The following literal string is the one way I could encode the icon inside the file for pyinstaller because it didn't like the external file
        # Possibly move this to another file in future to make the code cleaner
        # The icon was encoded to Base64 using the facility at this location https://www.motobit.com/util/base64-decoder-encoder.asp
        icon = \
        """AAABAAUAEBAAAAEAIABoBAAAVgAAABgYAAABACAAiAkAAL4EAAAgIAAAAQAgAKgQAABGDgAAMDAA
        AAEAIACoJQAA7h4AABgYAAABACAAiAkAAJZEAAAoAAAAEAAAACAAAAABACAAAAAAAAAEAAAAAAAA
        AAAAAAAAAAAAAAAAUmpLAFx6WDtFVjhgSVM2XlBaPF48Ri1eOkIoXkVNNF5RXT5eaG5TXjY7Jl5D
        TDReRk84XlNjR2BwjG07ZHtdAERUQgBPYkugOEU4/zU+NP03PzT9MTox/TA5Lv0wODD9N0E3/UBI
        Pv0zOzX9OUM9/TY+OP0+Szz/WG1ToExeSABETUoASFFEoUdRWf9HUVz/N0BK/z5HU/9ASVP/P0lQ
        /01XXv9IU17/TFdj/z5IUf8oLzP/LDUw/0VSPqE6RTgANz0zAD1DN6E5QDj/PkpZ/zdIhf9IXp7/
        UGSK/0tVUf9SXlr/UWeL/1JicP9NWl//WW6B/0FPTf9FUD+hPUk7AEFENABCRTehQEU+/0pdk/9d
        ecL/gZzH/6nD3f9seXL/Wmde/4am0f9xhpP/eYiE/6fF3/9ab27/RVY/oUBRQQBITTsAVVlFoUVP
        Tf9yjcD/gJer/36Ddf/Y39//g4p8/19nVv+6y9X/gI2I/2p0Yv+tvsT/YXBq/1NfSqFLWEgARlI5
        AFNfQ6FNXFH/mLTP/5uqrP9hZUz/hYqI/3J4bv90eWj/4OTf/4KJff9KVUb/sL23/2BtYP9FTzqh
        QU06AE5bPQBZZ0ehWmpX/6a/0P+isK3/WF9J/4+WmP+IkZX/jJCF/+Tm4//HzsX/pa+k/8HOwf9p
        eGb/QlE3oUNSOwBIVzgAVWJCoVtrVv++0Nn/qbWu/1dkSP+eppr/jp2f/5inm//V4d3/0dvR/7C7
        rv+zva//Y25c/0ZROqFFUDsAPkwwAFNeQaFNXUf/zdjR/7O9r/9UZEb/kpyC/3+Ndv9/jnn/x9HK
        /5yjm/9OW07/mqGW/2FrWP9LWT6hSFU9ADxHLwBdZkyhO0o0/7jIuf+ir6H/TWBN/8jTxf+DiXD/
        QEo0/62wqv+Pj4j/VmFU/5idlP9lbFv/W2ZOoVZgSgAtMyMAR0w8oSMtHP96koL/qb+x/5Kilv/F
        zr//Y2pU/zpEMP+pr6b/j5SJ/2hyZP+6v7P/aXBe/zlBL6FBSTcAJy0eAEBGNaISGQz/KTcn/218
        av+Hkn7/dYFp/y04Iv8yPSr/eYNz/3B6af9NVkb/hox9/15kUP9hak+iU1xDAIiQcACoso2PX2RN
        5kZHNuJOVj/iSlg/4kxYO+JIUjjiRE844kVSO+JGVTziQk014kJMNuJeak7mpLCKj4WScADGzqQA
        2eO0DqSoiBeHhHAXdHtiF1FeRRdsdlgXdH5hF2x5XhdYZ0oXSlw/F2NuUxdcZ00XgpJwF8PTpg6s
        vZQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAIABAACAAQAAgAEAAIABAACAAQAAgAEAAIABAACAAQAAgAEAAIABAACAAQAAgAEA
        AIABAACAAQAAgAEAAP//AAAoAAAAGAAAADAAAAABACAAAAAAAAAJAAAAAAAAAAAAAAAAAAAAAAAA
        ////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD/
        //8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wBefVvuSFk99jlE
        KPZQWj72V15B9kJPM/Y6Qy32ND0k9kNLMfZFTDb2Slc69l5oSPZ2emL2LTIf9jI5JPZNVz/2Rk86
        9kFKM/ZXZ0v2co9w7v///wD///8A////AP///wBPX0n3LDYv/yApJ/8kLCn/Jiwr/yApJ/8oMC//
        Iy0p/yErJ/8hKCf/ICkm/ykyMP8fKSf/Jy8u/zQ8Pf8uOjz/LTY3/y02N/8yPzP/U2dM9////wD/
        //8A////AP///wBCSzv2R1Fc/2Nug/9OV2H/SVFS/0JJTf9VXF7/VFtf/0VPV/8/SFT/UFpl/1Zg
        af9TXmT/W2Vw/1Zhcf9BSlP/MTY5/ygtMf8wOTT/QlA69v///wD///8A////AP///wBXX0/2Nj9D
        /01YYv83Qkr/KTVL/yMvTv80QF3/MT1W/zVAS/9MVFT/XGZj/0tZY/87Sl//RVRj/0FMUf80PUP/
        ICow/xokJv8rNCr/UV5L9v///wD///8A////AP///wA1OS/2Jyse/0VMO/8+TFz/OEmV/0FXs/9T
        a7z/W3Wz/09fcP9DSjf/TlZB/05hev9Wcaj/W2+J/1JaSP9PXm//d5Sy/3GKnP83Qzr/RU499v//
        /wD///8A////AP///wA7PjP2RUg1/ztDTf9DWaf/TmjL/2+S1v+Rteb/qc3z/5SruP9bZVf/VmBI
        /3eOpf+KtPn/bYyv/2ZrU/92jJb/r9T3/5GvyP81Rj7/T2BI9v///wD///8A////AP///wBWWEr2
        PUAv/0tYd/9gesn/f6Pd/1lmbv+JlZn/3e/+/7PGz/9ZYlL/PUUv/32Plv+wz/f/i6Gx/1peQf+R
        npf/yuH2/6i/z/83ST7/S11D9v///wD///8A////AP///wBeZE/2Nj0s/1Zqiv+EpOD/psTb/1VX
        Pf+EhG3////7/+Xr5v9scVr/RUox/5+pn//d7vf/nKqq/zxAI/9nc2H/tsPH/5Wkp/9EUUb/Zm9c
        9v///wD///8A////AP///wBZZUv2MDsl/26ElP+mx+z/tMfU/2JnT/9hZUz/iIqD/4KEgv9fYk//
        RUsy/7i9sP//////pK+o/yQpEP9PXlH/vsrG/52rpf8zPzH/TFJA9v///wD///8A////AP///wBe
        bU/2OUYr/4CXmv+vzuf/wNHc/292Wf9CRiz/ZW10/4iWpv97hHr/Y2hZ/7e5s///////sLqu/x4j
        F/9UYln/z9vS/7vIvf87TTn/Q1M29v///wD///8A////AP///wBkcVH2Qk0w/4edoP+sx+H/ytje
        /1tjSP9QV0b/oaWi/6qvtv9/h5L/foBv/7q7tf//////6vDp/93l2//N18z/xdLF/7jFtv8/TTr/
        S1pB9v///wD///8A////AP///wBdbEz2OUcp/5WoqP/D1+z/1N/i/05aP/9TX0b/wsq7/7jAyP+A
        kqD/jZqL/6m3sf/w+/r/4+vi/9jj1v/L1Mj/v8m7/6+7rP9HUkD/R1E69v///wD///8A////AP//
        /wBeakz2Lj4i/5uspP/k8ff/4Ofl/1ZnS/9FVTP/gopt/3qEeP+DmZL/prag/5uvpf/n9fH/y9TK
        /1dnWP9vem7/sbms/5KbjP8zPir/Ul5G9v///wD///8A////AP///wBhak72Hi4V/4qaif/n8ej/
        6e7n/05gQ/9XaEn/nqiM/52miv9qeVv/a3da/4+dj//i6OX/ycvF/zE+MP82RDf/oqef/6OnnP9G
        UTv/RlY59v///wD///8A////AP///wBmb1T2EiEK/3aHdv/k7uH/5+zj/yY1Gv9IXUf/0N7V/+br
        2/9iaUr/GSYL/36Kef/Jxsb/ubCv/0hOQP9PXlH/pKii/4CCev9XYEv/eohq9v///wD///8A////
        AP///wB6g2v2FR0I/1htW/+81MX/1ubb/ylBM/9edWn/ztrQ/9jby/9aXET/ERgC/295bf+6u7n/
        pqWe/0FLO/9seGr/t7yx/5ebjv9BRzb/PkI29v///wD///8A////AP///wBGSj32DBEC/yw+Lf+H
        pZX/vdbI/67CtP+rtqv/0dnM/7fAq/8vOSL/GiQN/4KNff+/w7z/vsK5/0RPPv9weW3/0dbL/7i7
        rP9KUz7/N0It9v///wD///8A////AP///wAjKRz2AwcA/w8bC/8+UkH/iJ2L/5qll/+nsJz/q7eg
        /2JuV/8ZJA7/HikV/36JeP+mr6D/oqud/0xVRf9galz/vcG0/7e7q/9GTDj/WGNJ9v///wD///8A
        ////AP///wCJk3b3GiEO/wUJAP8LDwD/KTIc/zxFM/9NXED/O0os/xokDv8kLhf/HScU/yErGf89
        SDX/VGBL/yw1Iv8fKhX/MTgm/y00I/82Pyf/k5p79////wD///8A////AP///wDM1qruk5l59mNi
        UfZxblv2e4Fn9j9MNvZWZEr2YW1O9l9oS/Zkb1T2YW5U9lJeRfZSYUb2R1k99klYP/ZdZkz2WWNK
        9kVSOvaCknD2vcug7v///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A
        ////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD/
        //8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
        /wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////
        AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A
        ////AP///wD///8A////AP///wD///8A////AMAAAwDAAAMAwAADAMAAAwDAAAMAwAADAMAAAwDA
        AAMAwAADAMAAAwDAAAMAwAADAMAAAwDAAAMAwAADAMAAAwDAAAMAwAADAMAAAwDAAAMA////AP//
        /wD///8AKAAAACAAAABAAAAAAQAgAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAABefVsAYIBd
        AVt4VwFLXkECPUouAkFLLwJRWj4CVl1BAkpVOAI+SjECOUIsAjU+JQI9RiwCREwzAkZNNgJJVjoC
        VmFCAmlxVAJscFkCNzwoAi0zHwI8RC4CTFY+AkdQOwJCSzUCSFM7AltsUAJuimsBdJJzAXKPcAAA
        AAAAAAAAAF9/XABggV42XHpYk0xgQpg/TC6YQ00wmFNdQJhZYEKYTFg5mEBMMZg6QyyYNj8lmD9H
        LJhGTjSYSFA3mExYO5hZZEOYbXVWmHB0XJg4PSiYLTMemD1FLZhOVz6YSVI7mENMNJhKVTuYXW9R
        mHCMbZN2lHU2dJFyAAAAAAAAAAAAWXNVAFt2V1tVbVH5QVE7/zI+Kv80PSr/QEk1/0RLOP87RTL/
        Mz4t/zI6K/8tNyb/Mjsp/zc+Lv83PzD/OUQx/0NOOf9QWET/T1VG/y81KP8tNCf/OEEz/0FLPf89
        Rzr/OkM2/z9KOf9OXkf/Y3xf+WmEZltngWMAAAAAAAAAAABNXEcAT19IWklYRfc0Pzj/KzQ0/yky
        Mv8qMjH/KzEw/ycvLf8oMTD/LjY1/yo0Mf8nMS7/Ji8t/yUtLf8mLy7/LTY1/yw2Nf8oMTH/LTY2
        /zU9QP82QEP/MDw+/y43OP8tNTf/Ljc1/zZDNv9NX0f3U2dLWlFkSgAAAAAAAAAAAEROPQBETjta
        RE1A9kNNU/9SXWz/VF5t/0hQWP9ETE7/P0ZJ/0NLTf9OVlj/TVVY/0VOU/89R0//PUZQ/0dRWv9O
        WGD/Tlhf/01XXf9TXWb/U11q/0tVYf88RU3/Mjg8/yswNP8rMTL/Mz01/0FQO/ZGVT1aRFM8AAAA
        AAAAAAAAUFhIAFJaSFpNVkn2QEpO/05ZZv9QW2j/P0lS/zZBTf8wOkv/NT5R/0BJW/8+SFj/O0ZS
        /z9JUf9LU1j/V2Fk/1RgZ/9LWGP/RlNh/0xZZ/9MV2P/Q05W/zY+Rf8mLjL/HSUo/yEpKP8wOjD/
        R1RC9k5cR1pLWUUAAAAAAAAAAABLUkQATVRFWkdOQvYzOjb/QEhH/0VPUf83Q1H/Ljxh/ys6bf8y
        Qnf/PU1+/z1Od/88S2L/QEtQ/0pSSv9VXlT/UF1j/0dYcP9EV3b/S1xw/0lVWf9CTE3/PUhT/z5O
        XP87S1b/NEJD/zM9M/9JVEP2T1pIWk1YRgAAAAAAAAAAADY6MAA3OzFaNDgt9i0xI/87QDH/Q01M
        /z5Nbf87TZX/Qliv/09nvP9ddsH/ZH+8/15zk/9RXmD/SE88/05WQf9SYWj/V2+V/115rv9ddJP/
        WGRg/1NdVf9abH3/eJSx/3uXsP9dcnv/OUU8/0ROPvZIUj9aRlE/AAAAAAAAAAAAOj0yADo9Mlo7
        PjL2QEMy/z5EP/8+S2n/RFmi/0pjv/9de83/dZfX/4yu4v+cv+n/lbDI/3iJi/9XYVH/VV9I/2Z3
        fP96l8H/gKfl/26Ns/9lcm7/Z3Bj/3iPnf+gwuL/nLza/2uEkP85ST//SlpF9k9fR1pOXUYAAAAA
        AAAAAABMTkIATU9DWkpNP/ZCRTT/QkpQ/0paiP9XccH/aYnU/2V/rv9whp//lqzB/8Pc8v+50OH/
        ipuc/1dhUf9JUjz/ZnV0/4ymxP+dwPD/hKC7/2l1av9tdGD/kaOm/7vW7f+zzub/eI+Y/zlLP/9I
        WkP2TWBFWkxeRAAAAAAAAAAAAFpdTQBcYE9aVVlI9j9DMv9GUV7/Wm6g/3KP1P+KrNv/anyH/2Rq
        Yf+WnZf/4evv/93q8P+irqr/XGNQ/0NKNP9rd23/obXB/7vU7f+YrLj/ZW5d/15kTP+MmZH/u83Y
        /7PH1f97jZD/QFBE/1FgS/ZXZk5aVWRNAAAAAAAAAAAAXWROAGBnUVpXXkn2O0Iw/0lYZP9rhK7/
        jazh/6PA2/90gHf/YGFG/46Pev/g4Nn/5+rn/6+1qv9lalP/Sk82/32EdP++ysf/2Ofu/6a0tP9a
        Yk//Q0ow/298bf+subn/p7a5/3WDgf9GU0b/XWdV9mVtWlpia1gAAAAAAAAAAABaZUwAXWhOWlRf
        RvY3QSz/U2Rn/4Gbt/+kw+j/sMbY/3+Jfv9eYkf/bHBZ/5GTiv+WmJX/f4J5/11hTP9JTzf/iY99
        /9XZ0v/v8/P/r7mz/1FYRf8wOCL/YG9i/6+7t/+uvLj/dYJ6/zlFN/9LU0H2UlhFWlBWRAAAAAAA
        AAAAAFxqTQBfbVBaVmRI9jtILv9ecGv/jqm6/6/N5/+5zdv/ipSH/1xhRP9QVT7/aG5s/3yEjf99
        hof/bXNl/1thT/+RlYn/2NnU//T19P+1vrX/SlFC/yQsHf9ebGL/ucW9/8HOxv+DkYX/Okk3/0NQ
        OPZGUjlaRVI5AAAAAAAAAAAAYW9QAGNyU1pbaUv2Qk8y/2d5cP+Urrv/sc3k/8HS3v+Mlof/V11B
        /01SP/9yeHn/jJah/42YoP97g3//cHRn/5qckv/W19T/9/n3/83VzP+FjIH/aXFn/4uXjf/CzsT/
        yNTJ/4yai/8+Tzr/RFQ59kZWOlpGVjoAAAAAAAAAAABjcFAAZnNTWl5rS/ZGUTT/bH50/5mxvf+z
        zOL/x9bf/4SOfv9QWD//XGNT/5qfmf+tsrX/nKOt/3+Ij/+AhHf/oaSZ/9TW0v/6/Pv/7PHr/+Ho
        3//W39T/zNbK/8XSxf/Azb7/i5iH/0JQPP9IVz/2S1pAWkpZQAAAAAAAAAAAAF5tTQBhb09aWWdH
        9j9NL/9wgXb/prvE/8PX6v/Q3OL/gIt7/0lVOv9hbFX/r7eo/73Fxf+irbj/gpGb/4qWi/+dqZ//
        x9LO//D59//m7uf/3efb/9Te0v/K08f/wcu+/7nFtv+JlIT/R1I//0dSO/ZIUjtaSFI7AAAAAAAA
        AAAAXWtMAGFuT1pXZEb2OUgr/3GCc/+0xcj/2ejy/9vk5v+FkoD/SVg6/1RiRP+Ol37/lp6T/4qY
        l/+Hm5r/m6yb/56vov+8zcf/5/Tw/9fg1/+ir6L/iJWH/5ihlf+yu63/qrSl/3aBcP89SDT/S1Y/
        9lBbQ1pOWUIAAAAAAAAAAABfak0AY25QWldiRfYwPyT/aXpo/7fGv//m8fH/5Ovn/4mWg/9KXD3/
        VGNC/4CKbP+HkHn/f4x7/36Rf/+Qn4j/k6ST/7TEvP/i7ej/zdXN/3SAc/9EUkT/Ym1h/6CnnP+l
        q5//dH1s/zxHMv9JVz32TlxCWk1aQAAAAAAAAAAAAGJrTwBnb1NaV2FG9iY1HP9bbFj/rryu/+fw
        5//o7ub/g5B7/0VYOf9fcFP/mqWL/6qzmf+Qm3//aHZY/2FuUf95h3P/rbiu/9zg3f/Ky8b/aXFm
        /y48Lv9IVUj/lJqS/6WpoP9+hHb/SVU+/0xbP/ZOXkBaTV1AAAAAAAAAAAAAZW5TAGx0WVpaY0n2
        Hy0W/05eS/+jsqP/5e7i/+bs4/9vemb/LT8k/1tvWf+4x7r/3eXW/7K4of9bY0X/LDgd/1pnUv+g
        p53/ysjH/722tf9vcWf/QUs9/1hlWf+YnZb/lJeQ/3F2af9ZY03/bnxf9nWDZVpzgWMAAAAAAAAA
        AAB1fmQAfIVrWmdwV/YhLBX/QFE+/42gkP/P4dP/2ufc/2V2Z/8qQC7/Y3lq/7/OxP/i6dz/s7ai
        /1RYPv8cJAz/S1VE/5OZkf+8u7n/rqqm/2hsYP9JVEX/bHhr/6Wqof+eoZf/cndp/0tSQP9UW0n2
        V15MWlZdSwAAAAAAAAAAAGlwXABvdmJaXGNP9h4lEv8uPSv/bIRz/67Iuf/J3dH/hJqN/2B2af+G
        mI3/xdDF/9Xczf+fpJD/Q0kx/xsjDP9OWEf/k5uR/7q8uP+wsqr/aG9h/0xXSP96hHf/t7yx/7S4
        rP+AhXX/Q0o4/zpAMfY4PjBaOD8wAAAAAAAAAAAAQUU4AEVJPFo5PjH2EhcJ/xklFv9HXUz/haGR
        /6/Iuf+xxrj/qrms/6+6rf/I0ML/vca0/32GcP8qNB3/HScQ/1lkUv+bpJf/vMG4/7q/tv9vd2n/
        TVhJ/3uEd//Cx7z/x8q9/4+Ug/9IUTz/PUcy9jpFMFo7RjEAAAAAAAAAAAAoLiEAKzEjWiMoHPYJ
        DgX/CxQH/yU1JP9RZlX/hZuJ/5mpmv+hrJz/qbKf/665pP+IlH7/TVhC/xwnEf8dKBT/WWRS/5Gb
        jP+psaP/pq6h/2t0Zf9OV0j/bndq/7O3q//AxLX/jZKA/0lQO/9RXEP2VWBGWlRfRQAAAAAAAAAA
        AGFpUwBncFhaVV1I9xgfEP8FCwD/ChIG/x4pGP9BTjr/VmFP/2VvXP9seV//Y3FW/0JONv8nMhz/
        HScR/xwmEv8yPCr/TlhH/2RuXf9ueWf/TFZE/zM8Kv86RTP/XGNS/2NoWP9PVUP/Qkoz/3N7X/eC
        im1afYVoAAAAAAAAAAAAprCNAKy3k1uZo4H5VVxC/zE1Jf8pKh3/MjQj/0JIMf8+RzL/QU03/0xb
        P/9GVDb/OEMo/zU+Jv87Ri7/N0Is/zI8KP82QSz/Q1A5/0tZQf8+SzX/ND8p/zU/KP86Qy3/ND0p
        /ztFL/9daEv/maOB+au0kFulrosAAAAAAAAAAADM1qoA0NqtS8TNo86aoH/VcnRd1WZjUtVycFzV
        eX5l1VRfR9VFUzvVV2VK1V9sTdVfaUzVYGpO1WNuVNVhblTVV2NK1VJeRdVQYEXVSVo+1UdYPtVQ
        XUTVXGVL1VljStVKVj7VWWdM1YmZdtW1w5nOwc+jS73LoAAAAAAAAAAAAM7YrADS3a8Mx9ClIJ6l
        gyF2eGEhaWdWIXZ0YCF8gWghVWBJIUVTPCFYZUshYW1PIWJsTiFjbVAhZnFWIWRwViFZZkwhU2BG
        IVFhRSFIWj4hSFg+IVJfRSFeaE4hW2VMIUtXPyFbaU0hjJx5IbfFmyDD0aUMvs2hAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAADwAAAA8AAAAPAAAADwAAA
        A8AAAAPAAAADwAAAA8AAAAPAAAADwAAAA8AAAAPAAAADwAAAA8AAAAPAAAADwAAAA8AAAAPAAAAD
        wAAAA8AAAAPAAAADwAAAA8AAAAPAAAADwAAAA8AAAAPAAAADwAAAA////////////////ygAAAAw
        AAAAYAAAAAEAIAAAAAAAACQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAX39cAF9/XABggV4NYIBdKlp3VTpPZUY6RVU4Oj1KLDpASy06TVc5OlVfQTpZYUI6VV4/OkpW
        ODpCTjI6PUcvOjlCKjo2PyU6OUEnOkFJLjpGTjM6R042OkhRODpLVzo6UV4+OlxnRTppclI6d3xh
        OmltVTpBRTA6LDIdOi81IDo5QSo6SFE4Ok5YPzpKUzw6Rk84OkNMNDpHUjg6U2FFOmB0VjpuiGo6
        dZNzKnaUdQ10knIAdJJyAAAAAAAAAAAAXn5cAF5+XABggF0rX39dh1l2VbdPY0W5RFQ3uD1JLLg/
        Si24S1Y5uFRdQLhYX0K4VFw+uElUN7hBTTK4PEcuuDlCKrg2Pia4OEEnuEBILrhFTDO4Rk01uEdQ
        N7hKVTm4UF0+uFplRbhncFG4dXpfuGdrVLhARDC4LDIeuC81ILg5QSq4R1E5uE1XP7hJUjy4RU44
        uEJLNLhHUTi4UmBFuF9zVrlth2i3dJJyh3WTdCtzkHEAc5BxAAAAAAAAAAAAW3ZXAFt2VwBceFk7
        W3dYulVtUP1HWkH/PEo0/jVAKv42QCr+QEoz/kdQOf5KUTv+R084/j5IMv44Qy/+NkAt/jM8K/4w
        OSb+Mjsm/jdAK/47Qy/+PEMx/jxFMv4+STP+Q083/kxWPv5VXkf+XmRQ/lRZR/44PS7+KzEi/i82
        Jv43Py/+QUs5/kRPPf5CSzv+P0g4/j1GNf5ASjj+SVdA/lZoTv9kfF/9bIdpum2IajtrhmgAa4Zo
        AAAAAAAAAAAAU2dOAFNnTgBVaVA8VGhPvEtdR/87SDn/Ljku/ycxJ/8mMCf/KzQr/y83Lv8xNy//
        LzYu/yozK/8oMir/KjMs/yozLP8nMSj/JjAn/ygxKP8pMin/KTEp/ykxKf8pMin/LDYs/zI8Mv81
        PjX/ND01/zA4Mf8qMSv/KjEs/zA3Mv80PDj/NUA7/zVAO/80PTn/Mzw3/zI7Nv80Pjb/OEU4/0NT
        QP9TaE7/XHNWvF10VzxbcVUAW3FVAAAAAAAAAAAAS1lFAEtZRQBNW0Y7TFpFu0VSQv84Qz3/MTs7
        /zA6Pf8vODz/Ljc4/y41Nv8uNTX/LDMz/ykxMf8qMzL/MDg4/zI6Ov8wOTj/LTc1/ys0M/8pMjL/
        KDAy/ygwMv8pMjT/LTY3/zE6O/8xOjv/LDY2/yw2Nv8xOjz/Nj9C/ztDSP86REn/NUBE/zE7P/8v
        Nzr/LTU3/yw0Nv8sNTX/Lzoz/zhGOP9HWEL/T2FHu1BjSDtOYEcATmBHAAAAAAAAAAAARE8+AERP
        PgBFTzw7RU89u0NOQv5BS0z/RU9Z/09ZaP9QWmj/SFFb/0NLUP9BSUv/P0ZH/ztCRP8+RUf/R05P
        /0tSU/9KUVP/Rk5R/z9JTf86REv/OEFJ/zpDTP9ASlL/Rk9X/0lTWv9JU1n/R1FW/0hSV/9NVl3/
        T1li/09ZZf9KVGD/QUtU/zlCSP8zOj7/LjQ3/yswNP8qMTP/Ljcz/zVBNv9ATjv+RlY+u0dWPjtF
        VT0ARVU9AAAAAAAAAAAAR1BAAEdQQABHUD47R1A/ukZPRf5ETVH/S1Vi/1lkdv9bZnf/T1ll/0dQ
        Wf9ETVP/QEhP/zxETf8/R1H/SVFZ/05WXv9NVV3/SVJb/0ROV/9BS1T/QktV/0dQWv9QWmL/VV9n
        /1VfaP9TXmf/T1tk/1BcZv9VYGv/VmFu/1NebP9NWGT/Q0xW/zlBSP8wNzv/KS8y/yUqLv8lLC3/
        KzMw/zQ/Nf9ATTv+RlQ+ukdVPztFUz4ARVM+AAAAAAAAAAAAU1tLAFNbSwBUXEs7U1tLukxVSv5A
        SUr/QUpT/05YZf9PWmb/Q05X/zpETv80Pkz/LzpL/ys2S/8uOVD/OEJY/zxGW/86RVj/OUNU/zhD
        UP89R0//RU5T/05XWf9XYGL/WGNm/1JeZf9LWGP/RFFh/0NRYf9IVmX/Sldk/0hUXf9DTVX/O0RL
        /zI6QP8nLzX/ICgs/xwlKP8fJyf/JzAq/zU+M/9GUkH+TlxIulBdSTtNW0cATVtHAAAAAAAAAAAA
        T1ZIAE9WSABRWEk7UFdIukhPRP44QDz/N0BA/0VOUP9HUVX/PUhP/zVBUP8uO1j/Kjhe/yk3Y/8t
        O2n/NkRw/zpJcv86SW7/OUhl/zlGWf8+SFD/Rk5N/05WUP9WX1f/VmFe/09dZf9IWGr/QlRu/0JU
        b/9HWG3/SVdk/0ZSVf9CTE3/PEZN/zhDTf81Q07/MkFL/y8+Rf8uOjz/LTgy/zZANP9GUkH+T1tJ
        ulBcSjtOWkgATlpIAAAAAAAAAAAAPUI3AD1CNwA/RDg7PkM3ujg9Mv4uMyn/MDYs/0BHPP9FTkj/
        P0tR/zlHYP81RHf/NEWI/zdJlP88UJ3/RVqi/0tho/9OZJ//TWKO/0lac/9GU1r/RU5G/0hPP/9O
        VkX/UFtT/05daf9MYH3/TWSO/1Bnkf9TaIb/U2Nx/09aVf9LVU7/SFRb/01eb/9acIf/YHiP/150
        hf9RZGz/PUtH/zhDN/9DTD3+SVJBuklTQTtIUkAASFJAAAAAAAAAAAAANTkvADU5LwA2OTA7NTkv
        ujM3LP4vMyX/Mzco/z1DNv9CS0n/QE5i/z5PfP89T5f/QFWr/0lhuf9TbcP/XnnI/2aCyv9sicf/
        a4a1/2R5k/9aaXD/TlhN/0pRPf9OVj//Ul1S/1ZndP9bcpX/YH2y/2KAtf9heqD/XXCA/1lkWv9X
        YFP/V2Vr/2R5jf97mLX/haTC/4CctP9qgY7/R1dV/zlGOv9CTT3+SFJAukhTQDtHUj8AR1I/AAAA
        AAAAAAAAODwxADg8MQA4OzE7ODsxujo9MP48QC//PkI0/z1DP/8+SFr/QFGB/0JYoP9GXLX/TmjE
        /118zf9sjtX/e53c/4iq4v+StOX/krLX/4miuP94ipD/YGxj/1RcSv9TXEX/WmZa/2d5hf9yjLD/
        ep3X/3ie2v9ujrn/Zn2P/2NtY/9jbFz/aHl7/3qTpf+WttT/n8Hi/5Oyzf91j5//SVxc/zlJPP9G
        VUH+TVxGuk5dRjtNW0UATVtFAAAAAAAAAAAAQkQ5AEJEOQBBRDk7QUQ5ukJFN/5DRjT/Qkc7/0BH
        Tf9BTW3/Rlqb/01mu/9Wccv/XnvN/2aEw/90ksP/h6XP/5u63/+vz/H/stDs/6W+z/+Mn6X/andv
        /1ZfTv9RWkP/WWZY/26Bif+BnLv/j7Po/42z7P99ncb/b4aW/2dxZP9pcV3/doaD/42lsv+qyeT/
        stPy/6LB2/9/mKj/TGBf/zlKPf9GWEL+T2BHuk9hRztOX0cATl9HAAAAAAAAAAAAT1JEAE9SRABQ
        UkY7UFJFuktOP/5DRjT/QUU+/0ROXP9LWoL/U2mt/197yv9tjdf/bozG/2N6nP9oe4//f5Gh/56y
        wv/C2Ov/y+H0/7fN2v+Xqa3/bXlw/1FaSP9GTjj/T1pL/2x9f/+In7T/nr3l/6DA6/+Oqcb/eYyV
        /2VuXf9nblb/f4uB/5uusv+50eP/wNrz/6/J3v+In6v/UGNg/zlLPP9FV0D+TF5Euk1fRDtLXkQA
        S15EAAAAAAAAAAAAWVtMAFlbTABbXU47WlxNulFUQ/5CRTT/P0U//0hUZ/9UZpL/Ynq8/3KQ1v+D
        pd7/fZq+/2Nzff9haWb/eYJ+/6Grqv/T3+X/4/H6/87e5f+pt7f/doB0/1NaRv9DSjP/TldG/3KA
        fP+UqLL/sMnj/7PN6v+cs8X/f4+Q/2BnU/9dY0n/eYNz/5mnpP+4y9X/wdXm/6/E0/+JnaT/U2Vg
        /z5OP/9LW0X+U2JKulNjSjtSYkkAUmJJAAAAAAAAAAAAXWFOAF1hTgBfZFA7XmNPulNYRf5ARjP/
        PUZA/0tabv9dcpz/cY3H/4Wl3/+Xt+D/jKW3/2Zxav9eYU3/dnlm/6Smmf/g49//9/39/+jw7//A
        yML/hIt6/1thSv9ITjX/VVxI/4CKf/+ntrb/xtnk/8fa6f+pusL/go6K/1ZdR/9MUTb/ZG5a/4WS
        if+rubz/tsbO/6W1vf+Dk5b/VWRe/0dURv9XY1H+YWxXumJtWDtga1cAYGtXAAAAAAAAAAAAXWRO
        AF1kTgBfZ1A7XmZPulJaRP49RTH/PEdA/1Bicv9ogKT/gZ/Q/5a25f+mw+H/lqyz/2t0ZP9dX0P/
        cHBX/5aWg//MzML/4uPf/9fb1v+2urH/goZ0/1xhSf9KTzX/WmBK/4yUhf+5wrz/2uXo/9jl6v+z
        wMH/g42F/01TPf88Qij/Ul1I/3eDd/+ksK7/s8DC/6Gvsf+Ajoz/VGFY/0ZRRP9XYE/+YmlXumNq
        VztgaFYAYGhWAAAAAAAAAAAAWmVMAFplTABdZ047XGZNuk9aQf46RC3/PUk+/1lrdf92j6r/kbDW
        /6XE6f+vyN//na6z/3J7a/9eYkj/ZWhO/3l7Z/+Ymo7/paei/5+inv+NkIj/cHNj/1hcRv9ITTX/
        XWNN/5acjP/HzMT/6u/t/+bs7f+6xMH/goyC/0RLNf8vNh7/RlJA/258cf+ksaz/t8TC/6a0sf+B
        j4n/TltQ/zxGOP9LUkL+VFpIulVbSDtTWUcAU1lHAAAAAAAAAAAAWmdMAFpnTABdak47W2hNuk9c
        Qf46Ri3/QE4//2F1eP+Bmq3/nbvZ/6/M6v+2zd//pLO2/3qCcv9gZUv/Wl5D/2FlUP9zd27/foKB
        /4GFh/97f33/bXFl/11iT/9PVT//ZGpW/5yhkv/N0Mj/8vLw/+3w7v/AyML/g4yA/z1EMf8mLRn/
        Pko8/2x6cP+otK7/wMzG/7C9t/+Ilo3/T1xP/zdDMv9CTDj+SlI9ukpSPTtJUT0ASVE9AAAAAAAA
        AAAAXWtOAF1rTgBfblA7XmxPulJgQ/4+SzD/RlVC/2l+e/+Jo6//osDX/7TQ6f+80eL/q7m7/4GK
        d/9hZ0r/T1Q4/1BUQf9hZ2P/cnmA/3+JlP+BjJL/eYF7/2xzZf9fZVT/cHRl/5+jmP/Mzsn/8fHw
        /+/x7//EzMT/ho+D/ztBM/8iKRv/Pko//299dP+vu7P/ytfO/77Lwv+VpJj/VmZV/zlJNP9ATjb+
        RVI4ukVTODtFUjgARVI4AAAAAAAAAAAAYG5QAGBuUABicVI7YW9RulZkRf5DUDP/S1pF/2+Dfv+O
        p7D/pMHV/7XQ5//A1OP/rry8/4GKd/9fZUj/S1E2/05TQ/9mbGr/e4OL/4qVov+MmKL/goyM/3d+
        dv9scmT/e39x/6Olnf/Mzcn/8fHw//P18v/S2dD/oame/2ZsYf9RWE7/ZXBm/4mWjP+4xLv/zdnP
        /8TQxf+cqpz/WmpZ/ztMNv9BUTf+RVU4ukVVODtFVTkARVU5AAAAAAAAAAAAY3BRAGNwUQBlc1M7
        ZHFSullmR/5HUzX/T11I/3OHgf+QqLH/o77U/7XO5f/E1uP/sLy7/3qDcP9YX0X/TlQ+/1xiU/+A
        hYD/l52f/5+mrv+aoar/h4+X/3uCgv93e3D/hoh6/6ipoP/Mzcn/8PDv//n7+f/n7Ob/0djP/7nB
        t/+utqz/rriu/7bBt//Cz8P/x9TH/8DNwP+bqZn/W2pY/z5NOP9FVDv+SVk/ukpZPztJWT4ASVk+
        AAAAAAAAAAAAYnBQAGJwUABlclI7ZHFRullmRv5HUzT/UV9J/3eKhP+VrLX/qMHV/7rR5v/J2eX/
        sb26/3R+av9SWkH/T1dC/2duX/+Vm5L/r7Sx/7G2uv+kqrT/i5Sg/36Hjf9/hXz/jpKD/6iso//I
        zMj/7O/u//n8+//v9e//6O/n/+Ts4v/e59z/1d/T/83YzP/H0sb/ws7A/7zJuv+appb/XWpY/0FO
        Ov9GVD3+SlhAuktYQDtKWD8ASlg/AAAAAAAAAAAAX21NAF9tTQBhcE87YG5OulVjQ/5CUDD/T15H
        /3uNhv+esrn/s8nb/8XY6//Q3uj/s766/3B7Z/9NWD3/TllA/2x2Yv+jq5z/vsW+/7vCxf+psr3/
        jZqo/4CPlv+FkYj/kZuO/6Oupf/AysX/5O3r//L6+P/r8uz/5Ozj/+Hq3//b5dn/093R/8zVyf/E
        z8H/vsq7/7jEtf+Xo5T/X2ta/0RPPP9GUTv+SFM7ukhTOztIUzwASFM8AAAAAAAAAAAAXWtMAF1r
        TABfbk47Xm1NulJhQf4+TC3/TFxE/36Phv+muLz/wNLg/9Hi8P/Y5Ov/t8G8/3F9aP9LWDz/S1g8
        /2hzWv+bpI//s7uu/662tP+fqrD/ipuk/4WXmv+PnpT/mKaX/6Cvpv+3xsH/3ern/+z38//j7OX/
        1N3T/8LNwP+3w7b/tsC0/7fBtP+7xLf/uMK0/6+6q/+Omor/WmVU/0JMOf9GUTv+SlQ9ukpUPTtK
        VD0ASlQ9AAAAAAAAAAAAXmpMAF5qTABgbU47X2xNulFfQP45SCv/SFhB/3+QhP+tvrz/zt3k/+Dt
        9f/h6u3/vMa+/3WDbv9NXT//R1c3/1pnSP+AiW3/kZmE/4yVif+Gk47/g5aU/4qemP+aq5v/oLGf
        /56wpP+xwrv/2Ofi/+bz7v/a5Nz/usW5/4yZjP94hnj/gIx//5KckP+qs6b/sLmr/6Ksnf+Ainr/
        TllG/ztGMv9IVD3+UFxEulFcRTtQW0MAUFtDAAAAAAAAAAAAX2pMAF9qTABibU87YGtOulBdP/40
        Qyf/QlI7/3qLfP+tvbb/1OLh/+nz9f/o7+7/wMnA/3eGcP9OX0H/SVk5/1hmRf94gmP/ho91/4KM
        eP9/i3z/fY+C/4SXiP+To47/mamU/5epmv+rvbT/1OLc/+Pu6f/V3db/qrSp/2h2aP9LWkz/VmNW
        /3J9cf+bo5f/q7Km/5+mmf9+h3f/TVdE/zpGMP9HVDz+T1xDulBdRDtPXEIAT1xCAAAAAAAAAAAA
        YGpNAGBqTQBkbVE7YmxPuk9bP/4vPSP/OUoz/3GCcP+mtan/09/Y/+v07//s8u3/w8vA/3WEbf9N
        X0H/T2BA/2NyUv+FkHP/lqCE/5SehP+KlXz/eIdv/3KCaP94hmv/gI51/4uaif+ntar/0dvW/+Ho
        5P/U2dP/pqyj/1pmWf81QzX/O0k7/1pmWv+OlYv/qK2j/6Sqnv+Ij4D/V2FO/0BMNf9FUzn+SFc7
        ukhYOztIVzsASFc7AAAAAAAAAAAAYmtPAGJrTwBnb1M7ZG1Ruk9aP/4qOB7/MUIr/2h5Zf+frp//
        0dzQ/+z06//u8+z/wcm8/2x6Yv9DVDf/S11A/2l5Xv+Wo4r/r7mh/7G6of+fqI3/eYVo/2FuT/9Y
        ZEf/YW5U/3yJd/+gq6D/ytDL/9vd2v/Pz8z/oqSd/1hgVP8yPjD/NUM1/1NgVP+JkIj/pKig/6Cj
        mv+HjH//XmZU/0tXP/9QX0P+U2NFulRkRjtTY0UAU2NFAAAAAAAAAAAAZG1SAGRtUgBpclY7Z3BU
        ulBaQP4mNBv/Kjok/19vXf+Xppf/zdnM/+v06f/t8+r/u8K1/1toUf8wQSX/P1I5/2l8Zv+ntqb/
        zdjK/9bdzP+7wqv/gYls/1JcPf82QiX/Pksy/2t4ZP+XoJT/vsG8/8/My//GwL//n5yX/19jWP8/
        STv/QlBC/15rX/+NlI3/n6Oc/5GUjP96fnP/X2dV/1lkTP9ndVn+cH5gunCAYTtvfV8Ab31fAAAA
        AAAAAAAAbHVaAGx1WgBxemA7b3hdulVfRf4mMhv/JTQf/1VmU/+LnIz/wtHC/+Lu4v/n8Ob/tb6x
        /1FgS/8nOiL/PFE8/22BcP+xwbb/2+bc/+Xr3v/Gy7j/g4dt/0pRNP8jLRL/KjYf/19qWP+Ol4v/
        tbay/8TAwP+7tbP/mZWP/2BkWP9HUEH/T1xO/2t3bP+WnJT/oqae/4+Siv93e2//XWRS/1dhS/9m
        cFj+bnlgum96YDtteF8AbXhfAAAAAAAAAAAAdoBnAHaAZwB9hm07eoNqul5nTv4rNB3/Iy8a/0pb
        Sf96j37/r8O0/9Hj1v/c6t//rr6x/1BjVP8rQTD/RVxN/3WJfP+ywrf/1+HX/9/k1v/Aw7D/foFp
        /0ZKMf8gJw7/Ji8a/1hiUv+Hj4X/ra+r/7y6uf+yr6v/kJCI/1thU/9IUkP/WmZX/3mEd/+hp53/
        rbGn/5uflP99gnT/V11N/0ZNO/9LUUD+TlREuk5URDtNVEMATVRDAAAAAAAAAAAAbnZhAG52YQB0
        fGc7cXlkuldfSv4oLxv/HigV/ztNOv9mfGv/mLGh/7zUxf/N4dX/sMS3/2qAc/9OZVj/Y3lt/4mb
        kP+5xrz/1N3R/9Xby/+zt6T/cHRe/z1BKv8dJA3/KDAc/1ljVP+Hj4X/rLCq/7u8uP+zs63/kZSK
        /1piU/9IU0T/YGtd/4OMgP+ss6f/ur6z/6quof+IjX7/WV9O/z9FNP87QTL+OkAyujo/Mjs6QDIA
        OkAyAAAAAAAAAAAAVFlJAFRZSQBYXU47VltLukJHOP4eJBP/FR4N/yo5KP9OZFP/fpmI/6O/sP+7
        1Mb/uM/B/5yypP+PopX/lKSY/6ezqf/EzsP/0NnL/8nQv/+gqJP/W2NM/y01Hv8bJA3/Ljgj/2Nt
        XP+PmIz/sLWt/8DDvf++wLn/m6CW/15nWP9KVUX/YWte/4eQhP+3vbL/yc3B/7u+sf+Xm4v/YWhV
        /0FKNv85QzD+N0AtujY/LTs3QC4AN0AuAAAAAAAAAAAAOz8zADs/MwA+QjY7PEE0ui4zJv4VGQ3/
        DRUH/xsoGf83Szr/YHpp/4Whkf+kva7/ssi6/6/Dtf+tva//rbir/7W+sf/Ezb7/w8y7/6+5pf+F
        j3n/RlA6/yErFf8aJQ7/Mz4p/2hzYf+TnI7/r7Wr/73Cuf+9wrj/naOX/2FqW/9MVkb/YGpc/4aO
        gv+4vrP/ztLG/8THuf+fo5P/ZWxY/0RNOP8/SjT+Pkkyuj1JMjs+STMAPkkzAAAAAAAAAAAAKC4h
        ACguIQArMCM7KS8iuh8kGf4NEQj/Bw0D/xAbDP8jMyL/QVVE/2J5aP+GnYz/m6+f/6Gwov+lsaL/
        qbOi/6+5pv+2wKz/qbSf/4mVfv9gbFX/Mj0n/xolD/8aJA//NUAs/2hzYf+PmYn/pa6g/7C4q/+v
        tqr/k5uO/2FqW/9OV0j/W2VX/32Gef+vtKj/x8u+/8LFtv+fo5L/Y2lW/0dOOf9LVT7+T1pBuk9a
        QTtPWkEAT1pBAAAAAAAAAAAAOkEwADpBMAA9RDM7PEMyuy00Jf4TGA3/BgwB/wgRBP8SHg//JDMj
        /z9PPv9fcV//dYVz/3+Le/+HkYD/jpiE/5Kdhv+RnYX/gIx0/15qU/9ASzT/JjEa/xkjDv8aJBD/
        Ljkm/1RfTf9xfGv/hI59/46YiP+Qmor/fYZ2/1ZfTv9ETT3/SlRE/2FqW/+IjoD/nKCS/5qej/+A
        hXT/VFpH/0hQOf9cZUz+aHJWu2lzVztmcFUAZnBVAAAAAAAAAAAAbnhfAG54XwB0fmQ7cXthu1hh
        Sv8pMB7/DBIE/wYMAf8IDgL/DxYI/x4nFv8zPir/Q046/01XRv9XYU7/X2xU/2BuU/9ZaEv/Slc8
        /zM/J/8lMBr/ISsV/x4oEv8cJhL/IiwZ/y85J/8+SDf/TlhH/1tmVP9kb1z/W2VS/0BJN/8wOSf/
        LTck/zZALf9JUD//UlhH/1BWRf9HTjz/PEMu/0pSOv9yel3/h49xu4mRczuEjG8AhIxvAAAAAAAA
        AAAAnKaFAJymhQCirIs8n6mIvISOb/9SWUD/LzUh/yElF/8dHxP/ICIU/yksGv81PCb/O0Qt/ztE
        MP8/SjX/SVc9/0taPf9FVDb/O0ks/y86IP8rNR3/MTsj/zM9Jv8vOiX/LTcj/ys1Iv8wOib/OkYx
        /0RRO/9MWkP/SVU//zpFMP8wOyb/LTgi/y85I/81PSn/Nj0q/zE5J/80PSn/QEsy/15pTP+Kk3P/
        oaqIvKStijyfp4UAn6eFAAAAAAAAAAAAvcefAL3HnwDCzKM7wMqhuq22kP2JkHD/am9W/lVXRP5O
        TT7+VFJB/lxcSP5jaFD+XGRM/kZRO/5BTjj+TVpB/lRiRv5WY0X+VGBC/k9ZPf5PWD3+U11D/lRf
        Rv5SXkX+TVpC/kdTPP5GUjr+Slc+/ktaQP5KWkD+R1c9/kNROf5EUTn+SlU8/k5XPv5OVz/+SVI7
        /kBLNP5IVDz+YW9S/oGPbf+ksYr9tsKaurjEmzu0wJgAtMCYAAAAAAAAAAAAztisAM7YrADS3K8r
        0NqticLLobqmrYm8io5xu3FxXbtoZlW6cG1bunh3Yrp9gWi6bnZduk5ZQrpDUTq6T11FulpnTLpg
        bE66Ym1PumJrTbpibE+6ZW9UumZxVrpkcVe6X2xSuldkSrpTYEa6U2FHulBgRLpJWz+6R1g9ukhZ
        P7pPXUO6WmRLul9oTrpcZky6VF9GuklWPbpUYke7dINku5Skf7yxwJe6wM6jicLQpCu+zaEAvs2h
        AAAAAAAAAAAA0NqtANDarQDU3rAO0tyvK8TNozupsIw8jZF1O3R0XztraVg7c3BdO3t6ZDuAg2s7
        cHhfO05aQztDUTo7UF5FO1poTDthbU87ZG9QO2NtTztlblE7Z3FWO2hzWDtmc1k7YW5UO1llTDtU
        YUc7VGJHO1BgRDtJWz87R1g9O0lZPztQXkU7XGZMO2BpTzteZ047VWBHO0pXPjtVY0g7doZmO5am
        gTyzwpg7wdCkK8PSpQ7AzqIAwM6iAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAD///////8AAOAAAAAABwAA4AAAAAAHAADgAAAAAAcAAOAAAAAABwAA
        4AAAAAAHAADgAAAAAAcAAOAAAAAABwAA4AAAAAAHAADgAAAAAAcAAOAAAAAABwAA4AAAAAAHAADg
        AAAAAAcAAOAAAAAABwAA4AAAAAAHAADgAAAAAAcAAOAAAAAABwAA4AAAAAAHAADgAAAAAAcAAOAA
        AAAABwAA4AAAAAAHAADgAAAAAAcAAOAAAAAABwAA4AAAAAAHAADgAAAAAAcAAOAAAAAABwAA4AAA
        AAAHAADgAAAAAAcAAOAAAAAABwAA4AAAAAAHAADgAAAAAAcAAOAAAAAABwAA4AAAAAAHAADgAAAA
        AAcAAOAAAAAABwAA4AAAAAAHAADgAAAAAAcAAOAAAAAABwAA4AAAAAAHAADgAAAAAAcAAOAAAAAA
        BwAA4AAAAAAHAADgAAAAAAcAAP///////wAA////////AAD///////8AAP///////wAA////////
        AAAoAAAAGAAAADAAAAABACAAAAAAAAAJAAAAAAAAAAAAAAAAAAAAAAAA////AP///wD///8A////
        AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A
        ////AP///wD///8A////AP///wD///8A////AP///wBefVvuSFk99jlEKPZQWj72V15B9kJPM/Y6
        Qy32ND0k9kNLMfZFTDb2Slc69l5oSPZ2emL2LTIf9jI5JPZNVz/2Rk869kFKM/ZXZ0v2co9w7v//
        /wD///8A////AP///wBPX0n3LDYv/yApJ/8kLCn/Jiwr/yApJ/8oMC//Iy0p/yErJ/8hKCf/ICkm
        /ykyMP8fKSf/Jy8u/zQ8Pf8uOjz/LTY3/y02N/8yPzP/U2dM9////wD///8A////AP///wBCSzv2
        R1Fc/2Nug/9OV2H/SVFS/0JJTf9VXF7/VFtf/0VPV/8/SFT/UFpl/1Zgaf9TXmT/W2Vw/1Zhcf9B
        SlP/MTY5/ygtMf8wOTT/QlA69v///wD///8A////AP///wBXX0/2Nj9D/01YYv83Qkr/KTVL/yMv
        Tv80QF3/MT1W/zVAS/9MVFT/XGZj/0tZY/87Sl//RVRj/0FMUf80PUP/ICow/xokJv8rNCr/UV5L
        9v///wD///8A////AP///wA1OS/2Jyse/0VMO/8+TFz/OEmV/0FXs/9Ta7z/W3Wz/09fcP9DSjf/
        TlZB/05hev9Wcaj/W2+J/1JaSP9PXm//d5Sy/3GKnP83Qzr/RU499v///wD///8A////AP///wA7
        PjP2RUg1/ztDTf9DWaf/TmjL/2+S1v+Rteb/qc3z/5SruP9bZVf/VmBI/3eOpf+KtPn/bYyv/2Zr
        U/92jJb/r9T3/5GvyP81Rj7/T2BI9v///wD///8A////AP///wBWWEr2PUAv/0tYd/9gesn/f6Pd
        /1lmbv+JlZn/3e/+/7PGz/9ZYlL/PUUv/32Plv+wz/f/i6Gx/1peQf+Rnpf/yuH2/6i/z/83ST7/
        S11D9v///wD///8A////AP///wBeZE/2Nj0s/1Zqiv+EpOD/psTb/1VXPf+EhG3////7/+Xr5v9s
        cVr/RUox/5+pn//d7vf/nKqq/zxAI/9nc2H/tsPH/5Wkp/9EUUb/Zm9c9v///wD///8A////AP//
        /wBZZUv2MDsl/26ElP+mx+z/tMfU/2JnT/9hZUz/iIqD/4KEgv9fYk//RUsy/7i9sP//////pK+o
        /yQpEP9PXlH/vsrG/52rpf8zPzH/TFJA9v///wD///8A////AP///wBebU/2OUYr/4CXmv+vzuf/
        wNHc/292Wf9CRiz/ZW10/4iWpv97hHr/Y2hZ/7e5s///////sLqu/x4jF/9UYln/z9vS/7vIvf87
        TTn/Q1M29v///wD///8A////AP///wBkcVH2Qk0w/4edoP+sx+H/ytje/1tjSP9QV0b/oaWi/6qv
        tv9/h5L/foBv/7q7tf//////6vDp/93l2//N18z/xdLF/7jFtv8/TTr/S1pB9v///wD///8A////
        AP///wBdbEz2OUcp/5WoqP/D1+z/1N/i/05aP/9TX0b/wsq7/7jAyP+AkqD/jZqL/6m3sf/w+/r/
        4+vi/9jj1v/L1Mj/v8m7/6+7rP9HUkD/R1E69v///wD///8A////AP///wBeakz2Lj4i/5uspP/k
        8ff/4Ofl/1ZnS/9FVTP/gopt/3qEeP+DmZL/prag/5uvpf/n9fH/y9TK/1dnWP9vem7/sbms/5Kb
        jP8zPir/Ul5G9v///wD///8A////AP///wBhak72Hi4V/4qaif/n8ej/6e7n/05gQ/9XaEn/nqiM
        /52miv9qeVv/a3da/4+dj//i6OX/ycvF/zE+MP82RDf/oqef/6OnnP9GUTv/RlY59v///wD///8A
        ////AP///wBmb1T2EiEK/3aHdv/k7uH/5+zj/yY1Gv9IXUf/0N7V/+br2/9iaUr/GSYL/36Kef/J
        xsb/ubCv/0hOQP9PXlH/pKii/4CCev9XYEv/eohq9v///wD///8A////AP///wB6g2v2FR0I/1ht
        W/+81MX/1ubb/ylBM/9edWn/ztrQ/9jby/9aXET/ERgC/295bf+6u7n/pqWe/0FLO/9seGr/t7yx
        /5ebjv9BRzb/PkI29v///wD///8A////AP///wBGSj32DBEC/yw+Lf+HpZX/vdbI/67CtP+rtqv/
        0dnM/7fAq/8vOSL/GiQN/4KNff+/w7z/vsK5/0RPPv9weW3/0dbL/7i7rP9KUz7/N0It9v///wD/
        //8A////AP///wAjKRz2AwcA/w8bC/8+UkH/iJ2L/5qll/+nsJz/q7eg/2JuV/8ZJA7/HikV/36J
        eP+mr6D/oqud/0xVRf9galz/vcG0/7e7q/9GTDj/WGNJ9v///wD///8A////AP///wCJk3b3GiEO
        /wUJAP8LDwD/KTIc/zxFM/9NXED/O0os/xokDv8kLhf/HScU/yErGf89SDX/VGBL/yw1Iv8fKhX/
        MTgm/y00I/82Pyf/k5p79////wD///8A////AP///wDM1qruk5l59mNiUfZxblv2e4Fn9j9MNvZW
        ZEr2YW1O9l9oS/Zkb1T2YW5U9lJeRfZSYUb2R1k99klYP/ZdZkz2WWNK9kVSOvaCknD2vcug7v//
        /wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////
        AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A
        ////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD/
        //8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
        /wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////
        AP///wD///8A////AMAAAwDAAAMAwAADAMAAAwDAAAMAwAADAMAAAwDAAAMAwAADAMAAAwDAAAMA
        wAADAMAAAwDAAAMAwAADAMAAAwDAAAMAwAADAMAAAwDAAAMA////AP///wD///8A"""

        icondata = base64.b64decode(icon)
        ## The temp file is icon.ico
        tempFile= "icon.ico"
        iconfile= open(tempFile,"wb")
        ## Extract the icon
        iconfile.write(icondata)
        iconfile.close()
        self.master.wm_iconbitmap(tempFile)
        ## Delete the tempfile
        os.remove(tempFile)


        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.master.mainloop()

    def createOptionsMenu(self):
        if not self.optionsMenu:
            self.optionsMenu = tk.Toplevel(self.master)
            self.optionsMenu.protocol("WM_DELETE_WINDOW", self.on_close_options)
            self.optionsMenu.title("Chat Display Options")

            self.f1 = tk.LabelFrame(self.optionsMenu, padx =5, pady=5)
            self.f1.grid()
            self.f2 = tk.LabelFrame(self.optionsMenu, text = "Player Info", padx =5, pady=5)
            self.f2.grid()
            self.f3 = tk.LabelFrame(self.optionsMenu, text = "Match Types", padx =5, pady=5)
            self.f3.grid()
            self.f4 = tk.LabelFrame(self.optionsMenu, text = "Faction Stats", padx =5, pady=5)
            self.f4.grid()
            self.f5 = tk.LabelFrame(self.optionsMenu, text = "Auto Trigger", padx =5, pady=5)
            self.f5.grid()            



            tk.Label(self.f1, text="Report Options").grid(sticky=tk.W)

            

            self.checkOwn = tk.Checkbutton(self.f2, text="Show Own Stats", variable=self.showOwn, command = self.saveToggles)
            self.checkOwn.grid( sticky=tk.W)
            self.checkWLRatio = tk.Checkbutton(self.f2, text="Country", variable=self.showUserCountry, command = self.saveToggles)
            self.checkWLRatio.grid( sticky=tk.W)
            self.checkWLRatio = tk.Checkbutton(self.f2, text="Steam Profile", variable=self.showSteamProfile, command = self.saveToggles)
            self.checkWLRatio.grid( sticky=tk.W) 


            #s1 = ttk.Separator(OptionMenu, orient=HORIZONTAL)
            #s1.grid()
            self.checkAutomaticMode = tk.Checkbutton(self.f3, text="AUTOMATIC MODE", variable=self.automaticMode, command = self.automode)
            self.checkAutomaticMode.grid( sticky=tk.W)

            self.checkBasic = tk.Checkbutton(self.f3, text="Basic Matches", variable=self.showBasic, command = self.saveToggles)
            self.checkBasic.grid( sticky=tk.W)
            self.check1v1 = tk.Checkbutton(self.f3, text="1v1 Matches", variable=self.show1v1, command = self.saveToggles)
            self.check1v1.grid( sticky=tk.W)
            self.check2v2 = tk.Checkbutton(self.f3, text="2v2 Matches", variable=self.show2v2, command = self.saveToggles)
            self.check2v2.grid( sticky=tk.W)
            self.check3v3 = tk.Checkbutton(self.f3, text="3v3 Matches", variable=self.show3v3, command = self.saveToggles)
            self.check3v3.grid( sticky=tk.W)
            #s2 = ttk.Separator(OptionMenu, orient=HORIZONTAL)
            #s2.grid()
            #self.frame1 = tk.Frame(self.master, text = "faction stats")
            #self.frame1.grid()
            self.checkWins = tk.Checkbutton(self.f4, text="Wins", variable=self.showWins, command = self.saveToggles)
            self.checkWins.grid( sticky=tk.W)
            self.checkLosses = tk.Checkbutton(self.f4, text="Losses", variable=self.showLosses, command = self.saveToggles)
            self.checkLosses.grid( sticky=tk.W)
            self.checkDisputes = tk.Checkbutton(self.f4, text="Disputes", variable=self.showDisputes, command = self.saveToggles)
            self.checkDisputes.grid( sticky=tk.W)
            self.checkStreak = tk.Checkbutton(self.f4, text="Streak", variable=self.showStreak, command = self.saveToggles)
            self.checkStreak.grid( sticky=tk.W)
            self.checkDrops = tk.Checkbutton(self.f4, text="Drops", variable=self.showDrops, command = self.saveToggles)
            self.checkDrops.grid( sticky=tk.W)
            self.checkRank = tk.Checkbutton(self.f4, text="Rank", variable=self.showRank, command = self.saveToggles)
            self.checkRank.grid( sticky=tk.W)
            self.checkLevel = tk.Checkbutton(self.f4, text="Level", variable=self.showLevel, command = self.saveToggles)
            self.checkLevel.grid( sticky=tk.W)
            self.checkLastPlayed = tk.Checkbutton(self.f4, text="Last Played", variable=self.showLastPlayed, command = self.saveToggles)
            self.checkLastPlayed.grid( sticky=tk.W)
            self.checkWLRatio = tk.Checkbutton(self.f4, text="W/L Ratio", variable=self.showWLRatio, command = self.saveToggles)
            self.checkWLRatio.grid( sticky=tk.W)

            self.checkAutomaticTrigger = tk.Checkbutton(self.f5, text="Automatic Trigger", variable=self.automaticTrigger, command = self.automaticTriggerToggle)
            self.checkAutomaticTrigger.grid( sticky=tk.W)


            self.automode() # setdisabled if auto on first run
        try:
            self.optionsMenu.focus()
        except Exception as e:
            logging.exception('Exception : ')

    def testStats(self):
        print("Testing Stats")
        if (self.thread):
            self.thread.queue.put('OPPONENT')


    def automaticTriggerToggle(self):
        if(bool(self.automaticTrigger.get())):
            if (self.thread):
                print("in automatic trigger toggle")
                self.automaticFileMonitor = COHOpponentBot_1.FileMonitor(self.parameters.data.get('logPath'),self.parameters.data.get('filePollInterval'), self.thread)
                self.automaticFileMonitor.start()
        else:
            if (self.automaticFileMonitor):
                print("trying to close automatic file monitor")
                self.automaticFileMonitor.close()
        self.saveToggles()        

    def automode(self):
        if (bool(self.automaticMode.get())):
            self.checkBasic.deselect()
            self.checkBasic.config(state = DISABLED)
            self.check1v1.deselect()
            self.check1v1.config(state = DISABLED)
            self.check2v2.deselect()
            self.check2v2.config(state = DISABLED)
            self.check3v3.deselect()
            self.check3v3.config(state = DISABLED)
        else:
            self.checkBasic.config(state = NORMAL)
            self.check1v1.config(state = NORMAL)
            self.check2v2.config(state = NORMAL)
            self.check3v3.config(state = NORMAL)
        self.saveToggles()

    def saveToggles(self):
        self.parameters.data['showOwn'] = bool(self.showOwn.get())

        self.parameters.data['automaticMode'] = bool(self.automaticMode.get())

        self.parameters.data['showBasic'] = bool(self.showBasic.get())
        self.parameters.data['show1v1'] = bool(self.show1v1.get())
        self.parameters.data['show2v2'] = bool(self.show2v2.get())
        self.parameters.data['show3v3'] = bool(self.show3v3.get())
        
        self.parameters.data['showWins'] = bool(self.showWins.get())
        self.parameters.data['showLosses'] = bool(self.showLosses.get())
        self.parameters.data['showDisputes'] = bool(self.showDisputes.get())
        self.parameters.data['showStreak'] = bool(self.showStreak.get())
        self.parameters.data['showDrops'] = bool(self.showDrops.get())
        self.parameters.data['showRank'] = bool(self.showRank.get())
        self.parameters.data['showLevel'] = bool(self.showLevel.get())
        self.parameters.data['showLastPlayed'] = bool(self.showLastPlayed.get())
        
        self.parameters.data['showWLRatio'] = bool(self.showWLRatio.get())

        self.parameters.data['showSteamProfile'] = bool(self.showSteamProfile.get())
        self.parameters.data['showUserCountry'] = bool(self.showUserCountry.get())

        self.parameters.data['automaticTrigger'] = bool(self.automaticTrigger.get())

        self.parameters.save()
        try:
            if self.thread:
                self.thread.parameters = self.parameters
        except Exception as e:
            logging.exception('Exception : ')

    
    def on_close_options(self):
        self.optionsMenu.destroy()
        self.optionsMenu = None

    def displayConsoleToggled(self):
        try:
            print(bool(self.consoleDisplayBool.get()))
            self.thread.displayConsoleOut = bool(self.consoleDisplayBool.get())
        except Exception as e:
            logging.exception('Exception : ')

    def disableEverything(self):
        self.b1.config(state = DISABLED)
        self.b2.config(state = DISABLED)
        self.b3.config(state = DISABLED)
        self.b4.config(state = DISABLED)
        self.b5.config(state = DISABLED)
        self.e1.config(state = DISABLED)
        self.e2.config(state = DISABLED)
        self.e3.config(state = DISABLED)
        self.e4.config(state = DISABLED)
        self.e5.config(state = DISABLED)
        self.connectButton.config(state = DISABLED)
        self.b6.config(state = DISABLED)
        self.testButton.config(state = DISABLED)

    def enableButtons(self):
        self.b1.config(state = NORMAL)
        self.b2.config(state = NORMAL)
        self.b3.config(state = NORMAL)
        self.b4.config(state = NORMAL)
        self.b5.config(state = NORMAL)
        self.connectButton.config(state = NORMAL)
        self.b6.config(state = NORMAL)
        #self.testButton.config(state = NORMAL)
        


    def editSteamNumber(self):  
        theState = self.e4.cget('state')
        if(theState == "disabled"):
            self.disableEverything()
            self.b4.config(state = NORMAL)
            self.e4.config(state = NORMAL)

        if(theState == "normal"):
            if self.checkSteamNumber(self.e4.get()):
                self.e4.config(state = DISABLED)
                self.enableButtons()
                self.parameters.data['steamNumber'] = self.e4.get()
                self.parameters.save()
            else:
                messagebox.showerror("Invaid Steam Number", "Please enter your steam number\nIt Should be an integer 17 characters long")
            
            # implement check value safe

    def editTwitchName(self):
        theState = self.e1.cget('state')
        if(theState == DISABLED):
            self.disableEverything()
            self.e1.config(state = NORMAL)
            self.b1.config(state = NORMAL)

        if(theState == NORMAL):
            if(self.special_match(self.e1.get())):
                self.e1.config(state = DISABLED)
                self.enableButtons()
                self.parameters.data['channel'] = self.e1.get()
                self.parameters.save()
            else:
                messagebox.showerror("Invalid Twitch channel", "That doesn't look like a valid channel name\nTwitch user names should be 4-24 characters long\nand only contain letters numbers and underscores.")

    def editBotName(self):
        theState = self.e2.cget('state')
        if(theState == "disabled"):
            self.disableEverything()
            self.b2.config(state = NORMAL)
            self.e2.config(state = NORMAL)

        if(theState == "normal"):
            if(self.special_match(self.e2.get())):
                self.e2.config(state = "disabled")
                self.enableButtons()
                self.parameters.data['botUserName'] = self.e2.get()
                self.parameters.save()
            else:
                messagebox.showerror("Invalid Twitch channel", "That doesn't look like a valid Twitch user name\nTwitch user names should be 4-24 characters long\nand only contain letters numbers and underscores.")

    def editOAuthKey(self):  
        theState = self.e3.cget('state')
        if(theState == "disabled"):
            self.disableEverything()
            self.b3.config(state = NORMAL)
            self.e3.config(state = NORMAL)

        if(theState == "normal"):
            if self.checkOAuthKey(self.e3.get()):
                self.e3.config(state = "disabled")
                self.enableButtons()
                self.parameters.data['botOAuthKey'] = self.e3.get()
                self.parameters.save()
            else:
                messagebox.showerror("Invaid OAuth Key", "Please enter your bots OAuth Key\nIt Should be an 36 characters long and start with oauth:\n You can find it here https://twitchapps.com/tmi/")



    def special_match(self, strg, search=re.compile(r'^[a-zA-Z0-9][\w]{3,24}$').search):
        if strg == "":
            return True
        return bool(search(strg))

    def checkOAuthKey(self, oauthkey):
        try:
            if (oauthkey[:6] == "oauth:") or (oauthkey == ""):
                return True
            return False
        except Exception as e:
            logging.exception('Exception : ')
            return False

    def checkSteamNumber(self, number):
        try:
            number = int(number)
            if isinstance(number, int):
                if (len(str(number)) == 17):
                    return True
            return False
        except Exception as e:
            logging.exception('Exception : ')

    def locateWarningLog(self):
        self.disableEverything()
        self.master.filename =  tk.filedialog.askopenfilename(initialdir = "/",title = "Select warning.log file",filetypes = (("log file","*.log"),("all files","*.*")))
        print(self.master.filename)
        if(self.master.filename != ""):
            self.parameters.data['logPath'] = self.master.filename.replace("/",'\\')
            self.e5.config(state = NORMAL)
            self.e5.delete(0, tk.END)
            logpath = self.parameters.data.get('logPath')
            if logpath:
                self.e5.insert(0, str(logpath))
            self.e5.config(state = DISABLED)
            self.parameters.save()
        self.enableButtons()



    def connectIRC(self, thread):
        if((self.checkSteamNumber(self.parameters.data.get('steamNumber'))) and (self.special_match(self.parameters.data.get('channel'))) and (os.path.isfile(self.parameters.data.get('logPath')))):
            self.disableEverything()
            self.b6.config(state = NORMAL)
            self.testButton.config(state = NORMAL)
            self.thread = COHOpponentBot_1.IRCClient(self.txt, bool(self.consoleDisplayBool.get()))
            self.thread.start()
            if (bool(self.parameters.data.get('automaticTrigger'))):
                self.automaticFileMonitor = COHOpponentBot_1.FileMonitor(self.parameters.data.get('logPath'),self.parameters.data.get('filePollInterval'), self.thread)
                self.automaticFileMonitor.start()
        else:
            messagebox.showerror("Invalid details", "Please check that your twitch username, Steam Number and warning.log file path are valid.")


    def on_closing(self):
        print("closing")
        try:
            if(self.thread):
                self.thread.close()
            if(self.automaticFileMonitor):
                self.automaticFileMonitor.close()
                self.automaticFileMonitor.event.set()
        except Exception as e:
            logging.exception('Exception : ')
        while (threading.active_count() > 1):
            pass
        print("exiting main thread")
        sys.exit()


# Program Entry Starts here
# Default error logging log file location:
logging.basicConfig(format='%(asctime)s (%(threadName)-10s) [%(levelname)s] %(message)s', filename= 'IRCOpponent_Temp_ERROR.log',filemode = "w", level=logging.DEBUG)
logging.info("Logging Started")
logging.info(VersionNumber)

main = COHBotGUI()