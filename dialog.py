# -*- coding: utf-8 -*-
#******************************************************************************
#
# demo
# ---------------------------------------------------------
# This plugin convert lesis GIS working dir structure to sqlite data base
#
# Author:   Alexander Lisovenko, alexander.lisovenko@nextgis.ru
# *****************************************************************************
# Copyright (c) 2015-2016. NextGIS, info@nextgis.com
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/licenses/>. You can also obtain it by writing
# to the Free Software Foundation, 51 Franklin Street, Suite 500 Boston,
# MA 02110-1335 USA.
#
#******************************************************************************

from PyQt4 import QtCore
from PyQt4 import QtGui

from qgis.gui import (
    QgsMapLayerComboBox,
    QgsMapLayerProxyModel,
    QgsFieldComboBox,
    QgsFieldProxyModel,
    QgsMessageBar
)

from qgis_plugin_base import Plugin
# from worker import Worker


class Dialog(QtGui.QDialog):
    def __init__(self, curPointLayerName, curPolygonLayerName, curFiledName, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.resize(300, 100)
        Plugin().plPrint("curPointLayerName:: %s" % curPointLayerName)
        Plugin().plPrint("curPolygonLayerName:: %s" % curPolygonLayerName)
        Plugin().plPrint("curFiledName:: %s" % curFiledName)
        self.setWindowTitle(Plugin().getPluginName())
        self.__mainLayout = QtGui.QVBoxLayout(self)
        self.__layout = QtGui.QGridLayout(self)

        # self.__layout.addWidget(QtGui.QLabel(self.tr("Point layer name") + ":"), 0, 0)
        l1 = QtGui.QLabel(u"Имя точечного слоя" + ":")
        l1.setSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Fixed
        )
        self.__layout.addWidget(l1, 0, 0)
        self.pointsLayersComboBox = QgsMapLayerComboBox()
        self.pointsLayersComboBox.setSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Fixed
        )
        self.pointsLayersComboBox.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.pointsLayersComboBox.setEditable(True)
        self.pointsLayersComboBox.setEditText(curPointLayerName)
        self.pointsLayersComboBox.layerChanged.connect(self.layerChooze1)
        self.__layout.addWidget(self.pointsLayersComboBox, 0, 1)


        # self.__layout.addWidget(QtGui.QLabel(self.tr("Field name") + ":"), 2, 0)
        self.__layout.addWidget(QtGui.QLabel(u"Имя поля" + ":"), 2, 0)
        self.fieldName = QgsFieldComboBox()
        self.fieldName.setFilters(QgsFieldProxyModel.Int)
        self.fieldName.setEditable(True)
        self.fieldName.setEditText(curFiledName)
        self.fieldName.fieldChanged.connect(self.filedChooze)
        self.__layout.addWidget(self.fieldName, 2, 1)

        # self.__layout.addWidget(QtGui.QLabel(self.tr("Polypon layer name") + ":"), 1, 0)
        self.__layout.addWidget(QtGui.QLabel(u"Имя полигонального слоя" + ":"), 1, 0)
        self.polygonsLayersComboBox = QgsMapLayerComboBox()
        self.polygonsLayersComboBox.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.polygonsLayersComboBox.setEditable(True)
        self.polygonsLayersComboBox.setEditText(curPolygonLayerName)
        self.polygonsLayersComboBox.layerChanged.connect(self.layerChooze2)
        self.polygonsLayersComboBox.layerChanged.connect(self.fieldName.setLayer)
        self.__layout.addWidget(self.polygonsLayersComboBox, 1, 1)

        # self.startButton = QtGui.QPushButton(self.tr("Start"))
        # self.startButton.clicked.connect(self.startCalculation)
        # self.__layout.addWidget(self.startButton, 3, 1)

        self.__mainLayout.addLayout(self.__layout)
        # self.progress = QtGui.QLabel()
        # self.__mainLayout.addWidget(self.progress)
        self.__bbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        self.__bbox.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.__bbox.accepted.connect(self.accept)
        self.__mainLayout.addWidget(self.__bbox)

    def layerChooze1(self, qgsMapLayer):
        self.pointsLayersComboBox.setEditText(qgsMapLayer.name())

    def layerChooze2(self, qgsMapLayer):
        self.polygonsLayersComboBox.setEditText(qgsMapLayer.name())

    def filedChooze(self, fieldName):
        self.sender().setEditText(fieldName)

    # def layernameSave(self, csTargetLayerName):
    #     if csTargetLayerName == u"":
    #         return
    #     setCSLayerName(csTargetLayerName)

    def getSettings(self):
        return [
            self.pointsLayersComboBox.currentText(),
            self.polygonsLayersComboBox.currentText(),
            self.fieldName.currentText()
        ]
    # def startCalculation(self):
    #     if self.fieldName.text() == "":
    #         self.showError(self.tr("Field name not set!"))

    #     pointLayer = self.pointsLayersComboBox.currentLayer()
    #     polygonLayer = self.polygonsLayersComboBox.currentLayer()

    #     worker = Worker(pointLayer, polygonLayer, self.fieldName.text())
    #     thread = QtCore.QThread(self)

    #     worker.moveToThread(thread)

    #     thread.started.connect(worker.run)
    #     worker.stoped.connect(thread.quit)
    #     worker.stoped.connect(worker.deleteLater)
    #     worker.stoped.connect(thread.deleteLater)
    #     worker.stoped.connect(self.close)
    #     worker.stoped.connect(self.showStopedMessage)
    #     worker.started.connect(self.showStartedMessage)
    #     worker.error.connect(self.showError)
    #     worker.progressChanged.connect(self.progressChanged)
    #     thread.start()

    #     self.thread = thread
    #     self.worker = worker

    # def showError(self, msg):
    #     Plugin().showMessageForUser(msg, QgsMessageBar.CRITICAL,)
    #     self.progress.setText(self.tr("Error: %s") % msg)

    # def showStartedMessage(self):
    #     self.progress.setText(self.tr("Initialization. Please wait..."))

    # def showStopedMessage(self):
    #     self.progress.setText(self.tr("Done!"))

    # def progressChanged(self, step, count):
    #     self.progress.setText(self.tr("Process %d polygones from %d") % (step, count))
