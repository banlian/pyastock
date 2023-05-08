import wx
import wx.grid

import threading
import time
import datetime

from qtrade.etrade_track.z_algo_rsi import get_stock_rsi
from qtrade.etrade_track.z_helper import get_stock_kline
from qtrade.etrade_track.z_track_rsi import RsiTrack, notifywin


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1500, 950))

        panel = wx.Panel(self)

        # rsi track obj
        self.rt = RsiTrack()
        self.rt.init()
        self.rt.logf = self.log
        self.rt.updatef = self.update_grid_rsi
        stockcount = len(self.rt.stocks)

        # rsi button
        self.btn_start_rsi = wx.Button(panel, label="start rsi", pos=(20, 20))
        self.Bind(wx.EVT_BUTTON, self.on_start_rsi, self.btn_start_rsi)
        self.btn_stop_rsi = wx.Button(panel, label="stop rsi", pos=(100, 20))
        self.Bind(wx.EVT_BUTTON, self.on_stop_rsi, self.btn_stop_rsi)
        self.btn_run_rsi = wx.Button(panel, label="run rsi", pos=(180, 20))
        self.Bind(wx.EVT_BUTTON, self.on_run_rsi, self.btn_run_rsi)

        self.checkbox = wx.CheckBox(panel, label='mode', pos=(260, 20))
        self.Bind(wx.EVT_CHECKBOX, self.on_mode_checked, self.checkbox)

        boxrsi = wx.StaticBox(panel, wx.ID_ANY, "rsi triggerd", pos=(20, 100), size=(600, 400))
        self.rsiret = wx.TextCtrl(boxrsi, style=wx.TE_MULTILINE, pos=(10, 20), size=(580, 370))

        boxinfo = wx.StaticBox(panel, wx.ID_ANY, "rsi info", pos=(20, 500), size=(600, 250))
        self.rsilog = wx.TextCtrl(boxinfo, style=wx.TE_MULTILINE, pos=(10, 20), size=(580, 220))

        # wx grid
        gridcols = ['stock', 'name', 'rsip', 'close1m', 'delta', 'close', 'pct', 'rsi30m']

        self.grid = wx.grid.Grid(panel, -1, pos=(660, 20), size=(800, 800))
        self.grid.CreateGrid(stockcount, len(gridcols))
        for c in gridcols:
            self.grid.SetColLabelValue(gridcols.index(c), c)

        for i in range(stockcount):
            s = self.rt.stocks[i]
            st = self.rt.stocknames[i]
            self.grid.SetCellValue(i, 0, s)
            self.grid.SetCellValue(i, 1, st)
            self.grid.SetReadOnly(i, 0)
            self.grid.SetReadOnly(i, 1)
            self.grid.SetColFormatFloat(2, 6, 2)
            self.grid.SetColFormatFloat(3, 6, 2)
            self.grid.SetColFormatFloat(4, 6, 2)
            self.grid.SetColFormatFloat(5, 6, 2)
            self.grid.SetColFormatFloat(6, 6, 2)
            self.grid.SetColFormatFloat(7, 6, 2)
            self.grid.SetCellValue(i, 2, str(0.0))
            self.grid.SetCellValue(i, 3, str(0.0))
            self.grid.SetCellValue(i, 4, str(0.0))
            self.grid.SetCellValue(i, 5, str(0.0))
            self.grid.SetCellValue(i, 6, str(0.0))
            self.grid.SetCellValue(i, 7, str(0.0))

        self.CreateStatusBar(6)  # A StatusBar in the bottom of the window

        # 创建定时器
        self.timer = wx.Timer(self)  # 创建定时器
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)  # 绑定一个定时器事件
        self.timer.Start(1000)

        # Setting up the menu.
        filemenu = wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard ids provided by wxWidgets.
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")  # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        r = get_stock_rsi('sh510050', n=10, count=60)
        self.SetStatusText(f'50etf: {r:.2f}', 4)
        r = get_stock_rsi('sh510300', n=10, count=60)
        self.SetStatusText(f'300etf: {r:.2f}', 5)

        # Set events.
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        self.thread = None

        self.Show(True)

    def update_grid_rsi(self, stock, rsi, close, delta, dclose, pct, rsi30m):
        r = self.rt.stocks.index(stock)
        # print('update grid', r)
        if r >= 0:
            if rsi is not None:
                self.grid.SetCellValue(r, 2, str(rsi))
            if close is not None:
                self.grid.SetCellValue(r, 3, str(close))
                c = wx.WHITE if self.rt.loopcount % 2 == 1 else wx.LIGHT_GREY
                self.grid.SetCellBackgroundColour(r, 3, c)
            if delta is not None:
                self.grid.SetCellValue(r, 4, str(delta))
                c = wx.GREEN if delta < self.rt.rsi_triggr else wx.YELLOW if delta < self.rt.rsi_threshold else wx.WHITE
                self.grid.SetCellBackgroundColour(r, 0, c)
                self.grid.SetCellBackgroundColour(r, 1, c)
                self.grid.SetCellBackgroundColour(r, 4, c)

            if dclose is not None:
                self.grid.SetCellValue(r, 5, str(dclose))
                pass
            if pct is not None:
                self.grid.SetCellValue(r, 6, str(pct))
                c = wx.RED if pct > 0 else wx.BLUE
                self.grid.SetCellTextColour(r, 6, c)
                pass

            if rsi30m is not None:
                self.grid.SetCellValue(r, 7, str(rsi30m))
                c = wx.RED if rsi30m < 25 else wx.GREEN if rsi30m > 75 else wx.WHITE
                self.grid.SetCellBackgroundColour(r, 7, c)
                pass
        pass

    def on_mode_checked(self, event):
        cb = event.GetEventObject()
        v = cb.GetValue()
        if self.rt is not None:
            if v:
                self.rt.mode = 0
            else:
                self.rt.mode = 1
        pass

    def on_start_rsi(self, event):
        if self.thread != None:
            self.rsilog.write('running')
            return
        self.rsilog.write('start rsi')

        self.thread = threading.Thread(target=self.run_rsi, name='rsi')
        self.thread.start()
        pass

    def run_rsi(self):
        self.rt.init()

        lastselected = []
        try:
            while self.rt.check():
                self.rsilog.Clear()

                # run rsi check
                selected, delay = self.rt.run()

                # process results
                self.rsiret.Clear()
                if len(selected) > 0:
                    for s in selected:
                        self.log_rsi(f'{s[0]} {s[5]:%H:%M:%S}')
                    self.save_rsi_last(selected)
                    self.Raise()

                if self.rt.mode == 1:
                    time.sleep(delay)
                    self.log(f'sleep {delay}s')
                else:
                    time.sleep(3)
        except Exception as ex:
            notifywin('rsi thread exit', 'rsi error' + str(ex))
            pass
        pass

    pass

    def on_stop_rsi(self, event):
        if self.thread is None:
            return

        self.rt.forcestop = True
        self.thread.join()
        self.rsilog.write('thread exit')
        self.thread = None
        pass

    def on_run_rsi(self, event):

        def run_once():

            self.rt.init()
            self.rt.manual = True

            self.rsilog.Clear()

            # run rsi check
            selected, delay = self.rt.run()

            # process results
            self.rsiret.Clear()
            if len(selected) > 0:
                for s in selected:
                    self.log_rsi(f'{s[0]} {s[5]:%H:%M:%S}')
                self.save_rsi_last(selected)
                self.Raise()

            self.rt.manual = False

        self.thread = threading.Thread(target=run_once, name='rsionce')
        self.thread.start()

        pass

    def log(self, log):
        self.rsilog.write(log + '\n')
        self.rsilog.ScrollLines(1)

    def log_rsi(self, log):
        self.rsiret.write(log + '\n')
        self.rsiret.ScrollLines(1)

    def OnTimer(self, evt):
        # 显示时间事件处理函数
        t = time.localtime(time.time())
        dt = time.strftime("%Y-%m-%d %H:%M:%S", t)
        self.SetStatusText(dt, 0)  # 显示年月日

        if datetime.datetime.now().second % 7 == 0:
            d0 = get_stock_kline('sh000001')
            d1 = get_stock_kline('sz399006')
            if d0 is not None:
                self.SetStatusText('sh:{:.2f}'.format(d0['close'][0]), 2)
            else:
                self.SetStatusText('', 2)
            if d1 is not None:
                self.SetStatusText('cyb:{:.2f}'.format(d1['close'][0]), 3)
            else:
                self.SetStatusText('', 3)

        if datetime.datetime.now().second % 20 == 0:
            r = get_stock_rsi('sh510050', n=10, count=60)
            self.SetStatusText(f'50etf: {r:.2f}', 4)
            r = get_stock_rsi('sh510300', n=10, count=60)
            self.SetStatusText(f'300etf: {r:.2f}', 5)
            pass

    def OnAbout(self, e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog(self, "A small text editor", "About Sample Editor", wx.OK)
        dlg.ShowModal()  # Show it
        dlg.Destroy()  # finally destroy it when finished.

    def OnExit(self, e):
        self.timer.Stop()
        self.Close(True)  # Close the frame.

    def save_rsi_last(self, lastselected):
        with open('lastrsi.csv', 'w') as fs:
            for s in lastselected:
                fs.write(','.join([str(v) for v in s]) + '\n')

        pass


if __name__ == '__main__':

    try:
        app = wx.App(False)
        frame = MainWindow(None, "rsi")
        app.MainLoop()
    except Exception as e:
        print(e)
        notifywin('rsi exit', 'rsi error')
        pass
