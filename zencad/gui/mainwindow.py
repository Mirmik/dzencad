import sys
import os
import time
import signal
import json
from zencad.util import print_to_stderr

import zencad.gui.actions
from zencad.gui.inotifier import InotifyThread
from zencad.gui.info_widget import InfoWidget
from zencad.gui.screen_saver import ScreenSaverWidget
from zencad.gui.console import ConsoleWidget
from zencad.gui.text_editor import TextEditor
from zencad.gui.display_unbounded import start_unbounded_worker, spawn_sleeped_worker
from zencad.gui.startwdg import StartDialog


from zencad.gui.retransler import ConsoleRetransler
from zencad.gui.communicator import Communicator

from PyQt5 import QtCore, QtGui, QtWidgets, QtOpenGL

import zencad.configuration
if zencad.configuration.FILTER_QT_WARNINGS:
    QtCore.QLoggingCategory.setFilterRules('qt.qpa.xcb=false')

class ZenClient:
    def __init__(self, communicator):
        self.communicator = communicator
        self.embeded_window = None
        self.embeded_widget = None

    def set_embed(self, window, widget):
        self.embeded_window = window
        self.embeded_widget = widget

    def pid(self):
        return self.communicator.subproc_pid()

class ZenFrame(QtWidgets.QMainWindow):
    def __init__(self, 
        title,
        sleeped_optimization=False,
        initial_communicator=None
    ):
        super().__init__()
        self.setWindowTitle(title)

        self._initial_client = None
        self._current_client = None
        self._sleeped_client = None
        
        self._sleeped_optimization = sleeped_optimization
        
        self.notifier = InotifyThread(self)

        self._keep_alive_pids = []

        # Reference Holder
        self._clients = {}

        if initial_communicator:
            self._initial_client = ZenClient(initial_communicator)
            self._current_client = self._initial_client

            initial_pid = self._initial_client.pid()
            self._clients[initial_pid] = self._initial_client
            self._keep_alive_pids.append(initial_pid)

        if self._sleeped_optimization:
            self.make_sleeped_thread()

    def init_zen_central_widget(self):
        self.console = ConsoleWidget()
        self.texteditor = TextEditor()
        self.screen_saver = ScreenSaverWidget()
        
        self.cw = QtWidgets.QWidget()
        self.cw_layout = QtWidgets.QVBoxLayout()
        self.hsplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.vsplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)

        self.cw_layout.addWidget(self.hsplitter)
        self.cw.setLayout(self.cw_layout)

        self.hsplitter.addWidget(self.texteditor)
        self.hsplitter.addWidget(self.vsplitter)
        self.vsplitter.addWidget(self.screen_saver)
        self.vsplitter.addWidget(self.console)

        self.cw_layout.setContentsMargins(0, 0, 0, 0)
        self.cw_layout.setSpacing(0)

        self.setCentralWidget(self.cw)
        self.update()

    def make_sleeped_thread(self, kill_prev=True):
        if self._sleeped_client and kill_prev:
            self._sleeped_client.subproc.terminate()

        self._sleeped_client = ZenClient(spawn_sleeped_worker())

    def central_widget_layout(self):
        return self.cw_layout

    def central_widget(self):
        return self.cw

    def init_changes_notifier(self, handler):
        self.notifier.changed.connect(handler)

    def finalize_subprocess(self, client):
        pid = client.pid()
        os.kill(pid, signal.SIGTERM)

    def subprocess_finalization_do(self):
        to_delete = []
        current_pid = self._current_client.pid()
        for pid in self._clients:
            if (
                    not pid == current_pid and
                    not pid in self._keep_alive_pids):
                self.finalize_subprocess(
                    client=self._clients[pid])
                to_delete.append(pid)

        for pid in to_delete:
            del self._clients[pid]
            
class MainWindow(ZenFrame, zencad.gui.actions.MainWindowActionsMixin):
    def __init__(self,
                 title="ZenCad",
                 initial_communicator=None
                 ):

        super().__init__(
            title=title,
            sleeped_optimization=zencad.configuration.SLEEPED_OPTIMIZATION,
            initial_communicator=initial_communicator)

        # Init objects
        self.info_widget = InfoWidget()
        
        # Init variables
        self._inited0 = False
        self._bind_mode = True
        self._current_opened = None
        self._openlock = QtCore.QMutex(QtCore.QMutex.Recursive)

        # Modes
        self._fscreen_mode = False

        # Init Gui
        self.createActions()
        self.createMenus()
        self.createToolbars()

        self.init_central_widget()
        
        # Bind signals
        self.init_changes_notifier(self.reopen_current)

    def init_central_widget(self):
        self.init_zen_central_widget()
        self.central_widget_layout().addWidget(self.info_widget)
        
        self.resize(640, 480)

    def showEvent(self, event):
        if not self._inited0:
            self.hsplitter.refresh()
            self.vsplitter.refresh()
            self.vsplitter.setSizes([self.height()*5/8, self.height()*3/8])
            self.hsplitter.setSizes([self.width()*3/8, self.width()*5/8])
            self.hsplitter.refresh()
            self.vsplitter.refresh()
            self._inited0 = True

    def reopen_current(self):
        self._openlock.lock()
        self.open(openpath=self._current_opened, update_texteditor=False)
        self.texteditor.reopen()
        self._openlock.unlock()

    def current_opened(self):
        return self._current_opened

    def open(self, openpath, update_texteditor=True):
        self._openlock.lock()

        self._current_opened = openpath
        if update_texteditor:
            self.texteditor.open(openpath)

        self.notifier.clear()
        self.notifier.add_target(openpath)

        need_prescale = False

        if self._sleeped_optimization:
            client = self._sleeped_client
            size = self.vsplitter.widget(0).size()
            size = "{},{}".format(size.width(), size.height())
            client.communicator.send({
                "cmd": "unsleep",
                "path": openpath,
                "need_prescale": need_prescale,
                "size": size
            })

            self.make_sleeped_thread(False)

        else:
            client = ZenClient(start_unbounded_worker(path=openpath,
                                                         need_prescale=need_prescale,
                                                         size=self.vsplitter.widget(0).size()))

        self._current_client = client
        self._clients[client.pid()] = client

        self._current_client.communicator.bind_handler(self.new_worker_message)
        self._current_client.communicator.start_listen()

        self._openlock.unlock()

    def open_declared(self, path):
        self._current_opened = path
        self.texteditor.open(path)

    def new_worker_message(self, data, procpid):
        try:
            cmd = data["cmd"]
        except:
            print("Warn: new_worker_message: message without 'cmd' field")
            returna

        if procpid != self._current_client.pid() and data["cmd"] != "finish_screen":
            return

        # TODO: Переделать в словарь
        if cmd == 'bindwin':
            self.bind_window(winid=data['id'], pid=data["pid"])
        # elif cmd == 'setopened':
        #    self.set_current_opened(path=data['path'])
        # elif cmd == 'clientpid':
        #    self.clientpid = data['pid']
        elif cmd == "except":
            print("!!!Exception:", data["header"])
        elif cmd == "qmarker":
            self.marker_handler("q", data)
        elif cmd == "wmarker":
            self.marker_handler("w", data)
        # elif cmd == "location":
        #    self.location_update_handle(data["loc"])
        # elif cmd == "keypressed":
        #    self.internal_key_pressed(data["key"])
        elif cmd == "keypressed_raw":
            self.internal_key_pressed_raw(
                data["key"], data["modifiers"], data["text"])
        # elif cmd == "keyreleased_raw":
        #    self.internal_key_released_raw(data["key"], data["modifiers"])
        elif cmd == "console":
            self.internal_console_request(data["data"])
        # elif cmd == "trackinfo":
        #    self.info_widget.set_tracking_info(data["data"])
        # elif cmd == "finish_screen":
        #    self.finish_screen(data["data"][0], data["data"][1], procpid)
        # elif cmd == "fault":
        #    self.open_fault()
        # elif cmd == "evalcache":
        #    self.evalcache_notification(data)
        else:
            print("Warn: unrecognized command", data)

    def bind_window(self, winid, pid):
        if self._current_client.pid() != pid:
            """Если заявленный pid отправителя не совпадает с pid текущего коммуникатора,
            то бинд уже неактуален."""
            print("Nonactual bind")
            return

        if not self._openlock.tryLock():
            return

        try:
            if self._bind_mode:
                window = QtGui.QWindow.fromWinId(winid)
                container = QtWidgets.QWidget.createWindowContainer(
                    window)
                self._current_client.set_embed(
                    window=window,
                    widget=container)
                self.vsplitter.replaceWidget(0, container)

            # Удерживаем ссылки на объекты, чтобы избежать
            # произвола от сборщика мусора
            self.setWindowTitle(self._current_opened)

            #self.open_in_progress = False

            #self._current_client_communicator.send({"cmd": "show"})

            # self.synchronize_subprocess_state()

            # time.sleep(0.1)
            # self.update()
        except Exception as ex:
            self._openlock.unlock()
            print_to_stderr("exception on window bind", ex)
            raise ex

        self.subprocess_finalization_do()
        self._openlock.unlock()

    def closeEvent(self, event):
        self.notifier.finish()
        self.notifier.wait()

    def internal_console_request(self, data):
        self.console.write(data)

    def internal_key_pressed_raw(self, key, modifiers, text):
        self.texteditor.setFocus()
        modifiers = QtCore.Qt.KeyboardModifiers()
        event = QtGui.QKeyEvent(
            QtCore.QEvent.KeyPress, key, QtCore.Qt.KeyboardModifier(modifiers), text)
        QtGui.QGuiApplication.postEvent(self.texteditor, event)

    def internal_key_released_raw(self, key, modifiers):
        modifiers = QtCore.Qt.KeyboardModifiers()
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyRelease,
                                key, QtCore.Qt.KeyboardModifier(modifiers))
        QtGui.QGuiApplication.postEvent(self.texteditor, event)


def start_application(openpath=None, none=False, unbound=False):
    QAPP = QtWidgets.QApplication(sys.argv[1:])
    initial_communicator = None

    if unbound:
        # Переопределяем дескрипторы, чтобы стандартный поток вывода пошёл
        # через ретранслятор. Теперь все консольные сообщения будуут обвешиваться
        # тегами и поступать на коммуникатор.
        retransler = ConsoleRetransler(sys.stdout)
        retransler.start()
    
        # Коммуникатор будет слать сообщения на скрытый файл,
        # тоесть, на истинный stdout
        initial_communicator = Communicator(
            ifile=sys.stdin, ofile=retransler.new_file)

        # Показываем ретранслятору его коммуникатор.
        retransler.set_communicator(initial_communicator)

        data = initial_communicator.simple_read()
        dct0 = json.loads(data)

        initial_communicator.declared_opposite_pid = int(dct0["data"])

    if openpath is None and not none and not unbound:
        if zencad.settings.list()["gui"]["start_widget"] == "true":
            strt_dialog = zencad.gui.startwdg.StartDialog()
            strt_dialog.exec()

            if strt_dialog.result() == 0:
                return

            openpath = strt_dialog.openpath

        else:
            openpath = zencad.gui.util.create_temporary_file(
                zencad_template=True)

    MAINWINDOW = MainWindow(
        initial_communicator=initial_communicator)

    if unbound:
        initial_communicator.bind_handler(MAINWINDOW.new_worker_message)
        initial_communicator.start_listen()

    if openpath:
        if not unbound:
            MAINWINDOW.open(openpath)
        else:
            MAINWINDOW.open_declared(openpath)

    MAINWINDOW.show()
    QAPP.exec()
