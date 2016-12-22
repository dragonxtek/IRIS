#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2016 Nicolás Boettcher
# This file is part of pythonCientifico_UdeC_2016-2
#
# pythonCientifico_UdeC_2016-2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pythonCientifico_UdeC_2016-2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License

from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui, QtCore
import webbrowser
import os.path
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx
import matplotlib.pyplot as plt
from influxdb import InfluxDBClient
import numpy as np

# Bulb mac
#  Single bulb
# mac = 'ea:9c:0f:a6:a0:20'
#  Double bulb
mac = 'd1:f1:98:fc:4e:a0'
mac2 = 'c4:bd:7c:27:89:be'
bulb = 0
enlace_bulb = False
# Host src
h1_index = 0
h1 = ''
# Host dst
h2_index = 0
h2 = ''
# Mininet configuration
src_index = 0
src = ''
dst_index = 0
dst = ''
#  Controller configuration
controller_ip = '127.0.0.1'
controller_port = '6633'
#  Grafana configuration
grafana_ip = '127.0.0.1'
grafana_port = '3000'
# Database configuration
host = 'localhost'
admin_port= 8083
port = 8086
user = 'admin'
password = 'admin'
dbname = 'sdn'
measurement = 'edges'
value="bw"
topology = 'None'
# Graph variable
grafo = 'g'
#  Variables
bw = 100
habilita = False
db_enabled = False
stp_enabled = False

fill = False
graphml = "None"


class AboutWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(AboutWindow, self).__init__(parent)

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.textBrowser = QtGui.QTextBrowser(self)
        self.textBrowser.append("By Nicolas Boettcher")
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.textBrowser)
        self.setWindowTitle("About")
        self.setGeometry(500, 500, 150, 50)


class StackedExample(QWidget):
    def __init__(self):
        super(StackedExample, self).__init__()
        self.leftlist = QListWidget()
        #  TODO save options to a file
        self.leftlist.insertItem(0, 'Mininet')
        self.leftlist.insertItem(1, 'Controller')
        self.leftlist.insertItem(2, 'Database')
        self.leftlist.insertItem(3, 'Bulb')
        self.leftlist.insertItem(4, 'Grafana')

        self.stack1 = QWidget()
        self.stack2 = QWidget()
        self.stack3 = QWidget()
        self.stack4 = QWidget()
        self.stack5 = QWidget()

        self.stack1ui()
        self.stack2UI()
        self.stack3UI()
        self.stack4UI()
        self.stack5UI()

        self.Stack = QStackedWidget(self)
        self.Stack.addWidget(self.stack1)
        self.Stack.addWidget(self.stack2)
        self.Stack.addWidget(self.stack3)
        self.Stack.addWidget(self.stack4)
        self.Stack.addWidget(self.stack5)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.leftlist)
        hbox.addWidget(self.Stack)

        self.setLayout(hbox)
        self.leftlist.currentRowChanged.connect(self.display)
        self.setGeometry(300, 300, 500, 10)
        self.setWindowTitle('Preferences')
        self.show()

    def stack1ui(self):
        layout = QFormLayout()
       # l1 = QLabel()
       # l1.setText("Hosts")
       # l1.setAlignment(Qt.AlignCenter)
       # layout.addWidget(l1)
       #  TODO sort nodes
        if grafo != 'g':
            self.mn1  =  QComboBox()
            tmp1 = []
            tmp2 = []
            tmp1.append('Elige origen')
            tmp2.append('Elige destino')
            for i in grafo.nodes():
                tmp1.append(i)
                tmp2.append(i)
            self.mn1.addItems(tmp1)
            self.mn1.setCurrentIndex(src_index)
            self.mn1.currentIndexChanged.connect(self.src_change)
            layout.addRow(QLabel("Origen"), self.mn1)
            self.mn2 = QComboBox()
            self.mn2.addItems(tmp2)
            self.mn2.setCurrentIndex(dst_index)
            self.mn2.currentIndexChanged.connect(self.dst_change)
            layout.addRow(QLabel("Destino"), self.mn2)

            # self.mn1.addItems(grafo.nodes())
            # self.mn1.setCurrentIndex(src_index)
            # self.mn1.currentIndexChanged.connect(self.src_change)
            # layout.addRow(QLabel("Origen"), self.mn1)
            # self.mn2  =  QComboBox()
            # self.mn2.addItems(grafo.nodes())
            # self.mn2.setCurrentIndex(dst_index)
            # self.mn2.currentIndexChanged.connect(self.dst_change)
            # layout.addRow(QLabel("Destino"), self.mn2)
        self.stack1.setLayout(layout)

    def stack2UI(self):
        # Execute your controller as follows:
        # ryu-manager --verbose --ofp-tcp-listen-port 6633 ryu.app.simple_switch_stp_13
        layout = QFormLayout()
        self.cip = QLineEdit()
        self.cip.setText(controller_ip)
        layout.addRow("address", self.cip)
        self.cip.editingFinished.connect(self.controller_ip_change)
        self.cport = QLineEdit()
        self.cport.setText(controller_port)
        layout.addRow("port", self.cport)
        self.cport.editingFinished.connect(self.controller_port_change)
        self.stack2.setLayout(layout)

    def stack3UI(self):
        #  TODO verificar que existe la bd
        layout = QFormLayout()
        client = QComboBox()
        client.addItems(["InfluxDB", "Graphite","OpenTSDB","Prometheus","ElasticSearch","CloudWatch"])
        for i in range(1,6):
            client.model().item(i).setEnabled(False)
        client.model().item
        layout.addRow(QLabel("Database"), client)
        self.ip = QLineEdit()
        self.ip.setText(host)
        layout.addRow("address", self.ip)
        self.ip.editingFinished.connect(self.db_ip_change)
        self.admin = QLineEdit()
        self.admin.setText(str(admin_port))
        layout.addRow("admin port", self.admin)
        self.admin.editingFinished.connect(self.db_admin_change)
        self.port = QLineEdit()
        self.port.setText(str(port))
        layout.addRow("server port", self.port)
        self.port.editingFinished.connect(self.db_port_change)
        self.db = QLineEdit()
        self.db.setText(dbname)
        layout.addRow("name", self.db)
        self.db.editingFinished.connect(self.db_db_change)
        self.table = QLineEdit()
        self.table.setText(measurement)
        layout.addRow("table", self.table)
        self.table.editingFinished.connect(self.db_table_change)
        value = QComboBox()
        value.addItems(["bw", "delay"])
        # TODO enable dynamic
        value.model().item(1).setEnabled(False)
        layout.addRow(QLabel("value"), value)
        self.user = QLineEdit()
        self.user.setText(user)
        layout.addRow("user", self.user)
        self.user.editingFinished.connect(self.db_user_change)
        self.password = QLineEdit()
        self.password.setText(password)
        layout.addRow("pass", self.password)
        self.password.editingFinished.connect(self.db_password_change)
        self.stack3.setLayout(layout)

    def stack4UI(self):
        layout = QFormLayout()
        self.cb = QComboBox()
        self.cb.addItems(["MagicBlue", "Philips"])
        self.cb.model().item(1).setEnabled(False)
        layout.addRow(QLabel("Brand"), self.cb)
        self.mac = QLineEdit()
        self.mac.editingFinished.connect(self.cambio_mac)
        layout.addRow("MAC", self.mac)
        if enlace_bulb:
            self.mac.setText(mac)
        else:
            self.mac.setEnabled(False)
        if grafo != 'g':
            self.h1 = QComboBox()
            tmp1 = []
            tmp2 = []
            tmp1.append('Elige origen')
            tmp2.append('Elige destino')
            for i in grafo.nodes():
                tmp1.append(i)
                tmp2.append(i)
            self.h1.addItems(tmp1)
            self.h1.setCurrentIndex(h1_index)
            self.h1.currentIndexChanged.connect(self.h1_change)
            layout.addRow(QLabel("Origen"), self.h1)
            self.h2 = QComboBox()
            self.h2.addItems(tmp2)
            self.h2.setCurrentIndex(h2_index)
            self.h2.currentIndexChanged.connect(self.h2_change)
            layout.addRow(QLabel("Destino"), self.h2)

        self.setLayout(layout)
        self.stack4.setLayout(layout)

    def stack5UI(self):
        layout = QFormLayout()
        self.gip = QLineEdit()
        self.gip.setText(grafana_ip)
        layout.addRow("address", self.gip)
        self.gip.editingFinished.connect(self.grafana_ip_change)
        self.gport = QLineEdit()
        self.gport.setText(grafana_port)
        layout.addRow("port", self.gport)
        self.gport.editingFinished.connect(self.grafana_port_change)
        self.stack5.setLayout(layout)

    def display(self, i):
        self.Stack.setCurrentIndex(i)

    def db_ip_change(self):
        global host
        host = self.ip.displayText()

    def db_admin_change(self):
        global admin_port
        admin_port = self.admin.displayText()

    def db_port_change(self):
        global port
        port = self.port.displayText()

    def db_db_change(self):
        global dbname
        dbname = self.db.displayText()

    def db_table_change(self):
        global measurement
        measurement = self.table.displayText()

    def db_user_change(self):
        global user
        user = self.user.displayText()

    def db_password_change(self):
        global password
        password = self.password.displayText()

    def controller_ip_change(self):
        print "La nueva ip es la ", self.cip.displayText()
        global controller_ip
        controller_ip = self.cip.displayText()

    def controller_port_change(self):
        print "El nuevo puerto es ", self.cport.displayText()
        global controller_port
        controller_port = self.cport.displayText()

    def grafana_ip_change(self):
        print "La nueva ip es la ", self.gip.displayText()
        global grafana_ip
        grafana_ip = self.gip.displayText()


    def grafana_port_change(self):
        print "El nuevo puerto es ", self.gport.displayText()
        global grafana_port
        grafana_port = self.gport.displayText()

    def src_change(self, i):
        print "El nuevo origen es el nodo ", self.mn1.currentText()
        global src,src_index
        src = self.mn1.currentText()
        src_index = i

    def dst_change(self, i):
        print "El nuevo destino es el nodo ", self.mn2.currentText()
        global dst,dst_index
        dst = self.mn2.currentText()
        dst_index = i

    def cambio_mac(self):
        if self.mac.isModified():
            print 'La nueva mac es '+self.mac.displayText()
            global mac
            mac = self.mac.displayText()
        self.mac.setModified(False)

    def h1_change(self, i):
        print "El nuevo origen es el nodo ", self.h1.currentText()
        global h1,h1_index
        h1 = self.h1.currentText()
        h1_index = i
        if self.check_link(str(h1), str(h2)):

            print 'Existe el enlace'

    def h2_change(self, i):
        print "El nuevo origen es el nodo ", self.h2.currentText()
        global h2,h2_index
        h2 = self.h2.currentText()
        h2_index = i
        if self.check_link(str(h1),str(h2)):

            print 'Existe el enlace'

    def check_link(self, hostA, hostB):
        global enlace_bulb
        for enlace in grafo.edges():
            if (hostA in enlace) and (hostB in enlace):
                #  Habilita el ingreso de una mac
                self.mac.setEnabled(True)
                self.mac.setText(mac)
                enlace_bulb = True
                return True
        #  Deshabilita el ingreso de mac
        self.mac.setEnabled(False)
        self.mac.setText('')
        enlace_bulb = False
        return False


class Console(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.edit  =  QTextEdit()
        self.edit.setReadOnly(True)
        # self.edit.setWindowTitle("QTextEdit Standard Output Redirection")
        self.button  =  QPushButton('Run Mininet')
        self.button.clicked.connect(self.onClick)
        layout  =  QVBoxLayout(self)
        layout.addWidget(self.edit)
        layout.addWidget(self.button)

        self.overlay = overlay(self.edit)
        self.overlay.hide()

    @pyqtSlot()
    def readStdError(self):
        # mininet uses StandardError
        self.edit.append(QString(self.proc.readAllStandardError()))

    def onClick(self):
        self.button.setEnabled(False)
        self.overlay.setVisible(True)
        #  Clean the console before display info
        self.edit.clear()
        timer = QtCore.QTimer(self)
        QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.loading)
        timer.start(1000)
        self.proc = QProcess()
        #  Bus::open: Can not get ibus-daemon's address.
        # IBusInputContext::createInputContext: no connection to ibus-daemon
        # To fix it, run ibus restart;ibus-setup
        global stp_enabled
        command = 'gksudo \"mn --switch ovsk --controller remote,ip=' + controller_ip + \
        ',port='+ controller_port + ' --custom topology.py --topo minimal --test pingpair'
        if stp_enabled:
            #  sudo mn --switch ovs --controller remote --topo tree,depth=2,fanout=2 --test pingpairdelay
            command = command + 'delay\"'
            # comando = 'gksudo \"mn --switch ovsk --controller remote,ip=127.0.0.1,port=6633 --custom topology.py --topo minimal --test pingpairdelay\"'
            print('Espere a que se ejecute STP')
        else:
            # comando = 'gksudo \"mn --switch ovsk --controller remote,ip=127.0.0.1,port=6633 --custom topology.py --topo minimal --test pingpair\"'
            command = command + '\"'
            print('Espere a que se ejecute')

        self.proc.start(command)
        self.proc.setProcessChannelMode(QProcess.MergedChannels)
        QObject.connect(self.proc, SIGNAL("readyReadStandardError()"), self, SLOT("readStdError()"))

    def loading(self):
        if int(self.proc.state())==0:
            self.button.setEnabled(True)
            self.overlay.setVisible(False)

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        event.accept()


class Qt4MplCanvas3(FigureCanvas):
    """Class to represent the FigureCanvas widget"""

    def __init__(self, parent):
        # plot definition
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        # Disable hold on
        self.axes.hold(False)
        self.compute_initial_figure()
        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)
        # set the parent widget
        self.setParent(parent)
        # we define the widget as expandable
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)

        def compute_initial_figure(self):
            pass

class MyDynamicMplCanvas3(Qt4MplCanvas3):
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, *args, **kwargs):
        Qt4MplCanvas3.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        # TODO same clock for bulb, refresh topology, generate
        QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
         er = nx.erdos_renyi_graph(0, 0)
         nx.draw(er, ax = self.axes)

    def update_figure(self):
        global habilita, graphml
        if habilita:
            ok = self.vis_top(graphml)
            if ok:
                self.get_fig()
        self.draw()

    def vis_top(self, filename_r):
        global habilita
        self.g = nx.read_graphml(filename_r)
        global grafo
        grafo = self.g
        self.color_nodos = '#00c8ff'
        self.vmin = 0
        self.pos = {}
        ejey = ''
        ejex = ''

        try:
            if self.g.node['0']['Latitude']:
                ejey = 'Latitude'
                ejex = 'Longitude'
        except:
            pass
        try:
            if self.g.node['0']['x']:
                ejex = 'x'
                ejey = 'y'

        except:
            pass
        # Si no posee niguno de los 2 labels anteriores no se ejecuta
        if ejex == '':
            print 'No se ha podido cargar la topologia, no posee coordenadas'
            QtGui.QMessageBox.information(self, QString.fromUtf8("Información"),
                                          QString.fromUtf8("""No se ha podido cargar la topologia, no posee coordenadas"""),
                                          QtGui.QMessageBox.Ok)
            habilita = False
            return 0

        try:
            # obtiene las coordenadas de cada nodo
            for node in self.g.nodes(data = True):
                self.pos[node[0]] = [node[1][ejex], node[1][ejey]]
        except:
            print 'No se pudo cargar, existen nodos sin coordenadas'
            QtGui.QMessageBox.information(self, QString.fromUtf8("Información"),
                                          QString.fromUtf8("""No se pudo cargar, existen nodos sin coordenadas"""),
                                          QtGui.QMessageBox.Ok)

            habilita = False
            return 0

        # obtiene los pesos de cada enlace
        self.bw = np.zeros(self.g.number_of_edges())
        self.order_sorted = np.zeros(self.g.number_of_edges())
        contador  =  0
        self.fig  =  plt.figure(figsize = (5, 4))
        global db_enabled
        if db_enabled == True:
            self.valor  =  self.lee_influxdb('bw', self.g.number_of_edges())
            if self.valor == 0:
                return 1
            # obtiene el orden de los enlaces
            self.order  =  self.g.edges()
            # ordena las tuplas de order
            for j in self.order:
                self.order[contador] = tuple(sorted(j))
                contador += 1
        return 1

    def get_fig(self):
        """
        Genera la figura a partir de la bd o valores por defecto
        """
        global db_enabled
        # Obtiene los valores de la bd
        if db_enabled == True:
            valor  =  self.lee_influxdb('bw', self.g.number_of_edges())
            # Verifica que existan valores en la bd
            if valor != 0:
                # obtiene los valores de la bd
                for i in valor:
                    hostA = int(i[1])
                    hostB = int(i[2])
                    hosts = (str(hostA), str(hostB))
                    try:
                        # busca la posicion de las tuplas y coloca el bw
                        self.bw[self.order.index(tuple(sorted(hosts)))] = int(i[3])
                    except:
                        print('no se encontro la ruta {} con la tupla {}').format(i, hosts)

        # Grafica los nodos host y switches preconfigurados
        #  Fix this issue: RuntimeWarning: More than 20 figures have been opened. Figures created through the pyplot interface (`matplotlib.pyplot.figure`) are retained until explicitly closed and may consume too much memory. (To control this warning, see the rcParam `figure.max_open_warning`).
        plt.close('all')
        nx.draw(self.g, self.pos, node_color = self.edges_color(src,dst), edge_color = self.bw, width = 4, edge_cmap = plt.cm.jet,
                edge_vmin = self.vmin, edge_vmax = bw, with_labels = True, ax = self.axes)

    def edges_color(self,src,dst):
        """
        Paint nodes as host or switches
        :param src: source host
        :param dst: destination host
        :return: list with all nodes
        """
        color_host = '#ff0000'
        color_switch = '#00c8ff'
        lista = []
        for i in self.g.nodes():
            if i == src or i == dst:
                lista.append(color_host)
            else:
                lista.append(color_switch)
        return lista

    def lee_influxdb(self, value = value, num = 1):
        client  =  InfluxDBClient(host, port, user, password, dbname)
        # result  =  client.query('select hostA,hostB,'+value+' from edges where time > now() - 1h limit '+str(num)+';')
        # print value+" "+measurement+" "+topology+" "+str(num)
        consulta = 'select src,dst,' + value + ' from ' + measurement + ' where topology  =  \'' + topology + '\' order by time desc limit ' + str(num) + ';'
        try:
            result = client.query(consulta)
            return result._get_series()[0].get('values')
        except:
            return 0

class overlay(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setPalette(QtGui.QPalette(QtCore.Qt.transparent))
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.movie_screen = QtGui.QLabel()

        # expand and center the label
        self.movie_screen.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Expanding)
        self.movie_screen.setAlignment(QtCore.Qt.AlignCenter)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(self.movie_screen)
        self.setLayout(main_layout)

        # use an animated gif file you have in the working folder
        # or give the full file path
        self.movie = QtGui.QMovie("icons/loader.gif", QtCore.QByteArray(), self)
        self.movie.setCacheMode(QtGui.QMovie.CacheAll)
        self.movie.setSpeed(100)
        self.movie_screen.setMovie(self.movie)
        self.movie.start()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor(255, 255, 255, 200))
        qp.drawRect(0, 0, 1000, 1000)
        qp.end()


class Ventana(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setGeometry(300, 300, 1000, 550)
        self.setWindowTitle("IRIS Monitoring Toolbox")
        #icono
        self.setWindowIcon(QtGui.QIcon('icons/logo.png'))
        bar  =  self.menuBar()
        file  = bar.addMenu("File")
        file.addAction("&Load...", self.getfile, "Ctrl+L")
        file.addSeparator()
        file.addAction('&Quit', self.close, "Ctrl+Q")
        tools  = bar.addMenu("Tools")
        tools.addAction("&Preferences", self.open_preferences, "Ctrl+P")
        win = bar.addMenu("Windows")
        win.addAction("&Graph", self.open_graph, "Ctrl+G")
        win.addAction("&Mininet", self.open_mininet, "Ctrl+M")
        help  =  bar.addMenu("Help")
        help.addAction("&About", self.about)

        self.statusBar = QStatusBar()
        self.b  =  QPushButton("click here")
        self.setWindowTitle("IRIS Monitoring Toolbox")
        self.setStatusBar(self.statusBar)
        self.createDockWindows()

    # def openFile(self):
    #     self.getfile()

    # def fileQuit(self):
    #     self.close()

    def open_graph(self):
        self.dock1.show()

    def open_mininet(self):
        self.dock2.show()

    def createDockWindows(self):
        plus = QtGui.QAction(QtGui.QIcon('icons/plus.png'), 'Add', self)
        play = QtGui.QAction(QtGui.QIcon('icons/play.png'), 'Play', self)
        self.play2 = play
        stop = QtGui.QAction(QtGui.QIcon('icons/stop.png'), 'Stop', self)
        self.stop2 = stop
        convert = QtGui.QAction(QtGui.QIcon('icons/network.png'), 'Convert', self)
        self.convert2 = convert
        stp = QtGui.QAction(QtGui.QIcon('icons/tree.png'), 'STP', self)
        self.stp2 = stp
        database = QtGui.QAction(QtGui.QIcon('icons/db.png'), 'Database', self)
        self.database2 = database
        generate = QtGui.QAction(QtGui.QIcon('icons/broadcast.png'), 'Generate', self)
        self.generate2 = generate

        toolbar = self.addToolBar('main')
        toolbar.addAction(plus)
        plus.triggered.connect(self.getfile)
        plus.setStatusTip('Open Topology')

        toolbar.addAction(play)
        play.triggered.connect(self.play)
        play.setStatusTip('Play On Real Time Topolgy traffic')
        play.setEnabled(False)

        toolbar.addAction(stop)
        stop.triggered.connect(self.stop)
        stop.setStatusTip('Stop On Real Time Topolgy traffic')
        stop.setEnabled(False)

        toolbar.addAction(convert)
        convert.triggered.connect(self.convert)
        convert.setStatusTip('Convert topology to Mininet format')
        convert.setEnabled(False)

        toolbar.addAction(stp)
        stp.triggered.connect(self.stp)
        stp.setStatusTip('Enable STP delay on Mininet')
        stp.setEnabled(False)

        toolbar.addAction(database)
        database.triggered.connect(self.database)
        database.setStatusTip('Connect to a database')
        database.setEnabled(False)

        toolbar.addAction(generate)
        generate.triggered.connect(self.generate)
        generate.setStatusTip('Generate random traffic')
        generate.setEnabled(False)

        bulb = QtGui.QAction(QtGui.QIcon('icons/bulb.png'), 'On', self)
        self.bulb2 = bulb
        toolbar2 = self.addToolBar('main')
        toolbar2.addAction(bulb)
        bulb.triggered.connect(self.lee_bulb)
        bulb.setEnabled(False)

        config = QtGui.QAction(QtGui.QIcon('icons/pref.png'), 'Preferences', self)
        about = QtGui.QAction(QtGui.QIcon('icons/about.png'), 'About', self)
        toolbar4 = self.addToolBar('main')
        toolbar4.addAction(config)
        config.triggered.connect(self.open_preferences)
        config.setStatusTip('Preferences')
        toolbar4.addAction(about)
        about.triggered.connect(self.about)
        about.setStatusTip('About')

        zoo = QtGui.QAction(QtGui.QIcon('icons/zoo.png'), 'Internet Topology Zoo', self)
        influxdb = QtGui.QAction(QtGui.QIcon('icons/influxdb.png'), 'Influxdb', self)
        grafana = QtGui.QAction(QtGui.QIcon('icons/grafana.svg'), 'Grafana', self)
        toolbar3 = self.addToolBar('main')
        toolbar3.addAction(zoo)
        zoo.triggered.connect(self.run_zoo)
        zoo.setStatusTip('Load The Internet Topology Zoo on your browser')

        toolbar3.addAction(influxdb)
        influxdb.triggered.connect(self.run_influxdb)
        influxdb.setStatusTip('Load InfluxDB on your browser')
        toolbar3.addAction(grafana)
        # grafana.setShortcut('Ctrl+G')
        grafana.triggered.connect(self.run_grafana)
        grafana.setStatusTip('Load Grafana on your browser')

        hbox = QHBoxLayout()
        self.main_widget = QtGui.QWidget(self)
        dc = MyDynamicMplCanvas3(self.main_widget)

        hbox.addWidget(dc)
        self.dock1 = QDockWidget()
        self.dock1.setWidget(dc)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dock1)
        self.dock1.widget().setMinimumSize(QSize(450, 400))

        #  INICIO 2ndo DOCK
        self.consola = Console()
        self.consola.button.setEnabled(False)
        hbox.addWidget(self.consola)
        self.dock2 = QDockWidget()
        self.dock2.setWidget(self.consola)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dock2)
        self.dock2.widget().setMinimumSize(QSize(450, 400))

    def about(self):
        # font = QtGui.QFont('SansSerif', 20)
        # msgbox = QtGui.QMessageBox()
        # msgbox.setFont(font)
        # msgbox.information(self, "Download Message", "Esto es un mensaje de \n prueba")
        QtGui.QMessageBox.about(self, "About", "<font color=\"black\" size=\"4\" face=\"Arial\"><pre>Copyright 2016 Nicol&aacute;s Boettcher<br />This program is for monitoring and create Mininet topologies.\n<br />It may be used and modified with no restriction; raw copies as well<br />as modified versions may be distributed without limitation.\n<br /><br /><img src=\"icons/github.png\" width=\"16\" height=\"13\" />  <a href=\"https://github.com/dragonxtek/IRIS\">https://github.com/dragonxtek/IRIS</a><br /><img src=\"icons/blogspot.ico\" width=\"16\" height=\"16\" />  <a href=\"https://installfights.blogspot.cl\">https://installfights.blogspot.cl</a><br /><img src=\"icons/twitter.png\" width=\"16\" height=\"16\" />  <a href=\"https://twitter.com/nicoboettcher\">@nicoboettcher</a><br /><img src=\"icons/gmail.png\" width=\"16\" height=\"16\" />  <a href=\"mailto:nicolas.boettcher@gmail.com?subject=Sent%20from%20IRIS\">nicolas.boettcher@gmail.com</a></pre></font>")


    def open_preferences(self):
        self.dialog = StackedExample()
        self.dialog.show()

    def play(self):
        global habilita
        habilita = True
        self.stop2.setEnabled(True)
        self.play2.setEnabled(False)

    def stop(self):
        global habilita
        habilita = False
        self.stop2.setEnabled(False)
        self.play2.setEnabled(True)

    def convert(self):
        if src=='' or dst=='':
            print 'Debe seleccionar dos hosts'
            QtGui.QMessageBox.information(self, QString.fromUtf8("Información"),
                                          QString.fromUtf8("""Debe seleccionar dos hosts"""),
                                          QtGui.QMessageBox.Ok)
        else:
            print('Conviertiendo...')
            global graphml

            # self.mininet_topology(graphml,False)
            self.mininet_topology(graphml)
            self.consola.button.setEnabled(True)
            self.stp2.setEnabled(True)

    @staticmethod
    def stp():
        global stp_enabled
        if stp_enabled:
            print 'Disabled STP'
            stp_enabled = False
        else:
            print 'Enabled STP'
            stp_enabled = True

    @staticmethod
    # TODO habilitar play solo cuando se habilite la BD
    def database():
        # TODO uncheck database if is stopped
        global db_enabled
        if db_enabled:
            print 'Disabled database'
            db_enabled = False
        else:
            print 'Enabled database'
            db_enabled = True

    def generate(self):
        global fill
        if fill:
            print 'Disabled data generation'
            fill = False
        else:
            print 'Enabled data generation'
            fill = True
            timer = QtCore.QTimer(self)
            QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update_db)
            timer.start(1000)

    def update_db(self):
        if fill:
            global grafo
            self.fill_edges(grafo)

    def lee_bulb(self):
        global bulb,enlace_bulb
        if enlace_bulb:
            if bulb == 0:
                print 'Enabled bulb'
                bulb = 1
                timer = QtCore.QTimer(self)
                QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update_bulb)
                timer.start(1000)
            else:
                print 'Disabled bulb'
                bulb = 0
        else:
            print 'Debe seleccionar un enlace para monitorear'
            QtGui.QMessageBox.information(self, QString.fromUtf8("Información"),
            QString.fromUtf8("""Debe seleccionar un enlace para monitorear"""),
            QtGui.QMessageBox.Ok)

    @staticmethod
    def update_bulb():
        #  TODO check bulb after generate traffic
        global bulb,enlace_bulb
        if enlace_bulb:
            comando = "influxdb2magicblue -m "+str(mac)+" -s "+str(h1)+" -d "+str(h2)+" -T "+str(topology)+" -t "+str(measurement)+" -D "+str(dbname)+" -a "+str(host)+" -p "+str(port)+" -u "+str(user)+" -P "+str(password)
            if bulb == 1:
                os.system(comando)

    def getfile(self):

        fname = QFileDialog.getOpenFileName(self, 'Open file',
        '/home/nboettcher/Doctorado/cursos/2016/2016-2/python/proyecto/final/',
                                                    "GraphML files (*.graphml)")
        #  Si se abre un archivo, entonces:
        if fname:
            print fname
            global grahpml,habilita

            tmp = str(fname)
            tmp2 = tmp.encode('ascii', 'ignore')
            global graphml
            graphml = tmp2
            global topology
            topology = graphml.split('.')[0].split('/')[-1]
            #  Resetea todas las variables
            global h1_index,h1,h2_index,h2,src_index,src,dst_index,dst,stp_enabled,db_enabled
            h1_index = 0
            h1 = ''
            # Host dst
            h2_index = 0
            h2 = ''
            # Mininet configuration
            src_index = 0
            src = ''
            dst_index = 0
            dst = ''
            stp_enabled=False
            db_enabled = False
            self.consola.button.setEnabled(False)
            habilita = True
            self.convert2.setEnabled(True)
            self.stop2.setEnabled(True)
            self.bulb2.setEnabled(True)
            self.database2.setEnabled(True)
            self.generate2.setEnabled(True)

    @staticmethod
    def remove_char(text):
        output = ''
        for i in text:
            # text without commas and spaces
            if not (i == ' ' or i == ','):
                output +=  i
        return output

    def mininet_topology(self,filename_r, filename_w='topology.py'):
        #  TODO load wireless topologies
        g = nx.read_graphml(filename_r)
        # Start to create filename_w
        archivo = open(filename_w, 'w')
        archivo.write('from mininet.topo import Topo\n')
        archivo.write('class MinimalTopo(Topo):\n')
        archivo.write('\tdef build(self):\n')
        archivo.write('\t\t#Create devices\n')

        # Initial DataPath ID
        dpid = 1000
        for i in g.node.keys():
            tmp = ''
            if not ('host' in g.node[i] or 'switch' in g.node[i]):
                if 'label' in g.node[i]:
                    tmp += self.remove_char(g.node[i]['label'])[:10]
                if 'cpu' in g.node[i]:
                    tmp += ',cpu = ' + g.node[i]['cpu']
                if i == src or i == dst:
                    archivo.write("\t\t%s  =  self.addHost('%s')\n" % (self.remove_char(g.node[i]['label'])[:10], tmp))
                else:
                    archivo.write("\t\t%s  =  self.addSwitch('%s',dpid = '000000000000%d')\n" % (
                    self.remove_char(g.node[i]['label'])[:10], tmp, dpid))
                    dpid +=  1

                # Set coordinates
                # Gephi standar
                if 'x' in g.node[i] and 'y' in g.node[i]:
                    g.node[i]['pos'] = (g.node[i]['x'], g.node[i]['y'])
                # Topology Zoo standar
                elif 'Latitude' in g.node[i] and 'Longitude' in g.node[i]:
                    g.node[i]['pos'] = (g.node[i]['Longitude'], g.node[i]['Latitude'])

        # Create links
        archivo.write('\t\t#Create links\n')
        for edge in g.edges(data=True):
            tmp = ''
            tmp += "'" + self.remove_char(g.node[edge[0]]['label'])[:10] + "','" + \
                                self.remove_char(g.node[edge[1]]['label'])[:10] + "'"
            # TODO enable compatibility with other mininet parameters
            # if 'bw' in edge[2]:
            #     tmp + =  ', bw = ' + edge[2]['bw']
            # elif 'LinkSpeed' in edge[2]:
            #     tmp + =  ', bw = ' + edge[2]['LinkSpeed']
            # if 'delay' in edge[2]:
            #     tmp + =  ', delay = ' + edge[2]['delay']
            # if 'loss' in edge[2]:
            #     tmp + =  ', loss = ' + edge[2]['loss']
            # if 'max_queue_size' in edge[2]:
            #     tmp + =  ', max_queue_size = ' + edge[2]['max_queue_size']
            # if 'use_htb' in edge[2]:
            #     tmp + =  ', use_htb = ' + edge[2]['use_htb']

            archivo.write("\t\tself.addLink(%s)\n" % (tmp))

        archivo.write('topos  =  {\n')
        archivo.write("\t'minimal': MinimalTopo\n")
        archivo.write('}')

        archivo.close()

    @staticmethod
    def run_grafana():
        url_grafana = 'http://'+grafana_ip+':'+grafana_port
        # Open URL in new browser window
        webbrowser.open_new(url_grafana)  # opens in default browser

    @staticmethod
    def run_influxdb():
        url_infludb = 'http://'+host+':'+str(admin_port)
        # Open URL in new browser window
        webbrowser.open_new(url_infludb)  # opens in default browser

    @staticmethod
    def run_zoo():
        url_zoo = 'http://topology-zoo.org/dataset.html'
        webbrowser.open_new(url_zoo)

    @staticmethod
    def connect():
        client = InfluxDBClient(host, port, user, password, dbname)
        # client.drop_database(dbname)
        client.create_database(dbname)
        return client

    def fill_by_edge(self, id1, id2):
        """
        ADD JSON with bw and delay to the bd between two nodes
        :param id1: node1
        :param id2: node2
        :return: None
        """
        client = self.connect()

        json_body = [
            {
                "measurement": measurement,
                "tags":
                {
                    "src": id1,
                    "dst": id2,
                    "topology": topology
                },
                "_comment": "time: 2009-11-10T23:00:00Z",
                "fields":
                {
                    "bw": np.random.randint(0, bw),
                    "delay": np.random.randint(0, bw)
                }
            }]
        # Send JSON to bd
        client.write_points(json_body)

    def fill_edges(self, g):
        """
        Agrega trafico random a todos los enlaces de un grafo
        :param g: graph
        :return: None
        """
        for i in g.edges():
            self.fill_by_edge(str(i[0]), str(i[1]))


def main():
    app = QtGui.QApplication(sys.argv)
    ventana = Ventana()
    ventana.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()