# -*- coding: utf-8 -*-
#******************************************************************************
#
# PointsInPolygons
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

from PyQt4 import QtCore, QtGui

from qgis.core import (
    QgsMapLayerRegistry,
    QgsApplication
)

from qgis.gui import (
    QgsBusyIndicatorDialog,
    QgsMessageBar
)

from qgis_plugin_base import Plugin
from dialog import Dialog
from worker import Worker


class PointsInPolygons(Plugin):
    def __init__(self, iface):
        Plugin.__init__(self, iface, "PointsInPolygons")

        userPluginPath = QtCore.QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + '/python/plugins/points_in_polygons'
        systemPluginPath = QgsApplication.prefixPath() + '/python/plugins/points_in_polygons'

        overrideLocale = QtCore.QSettings().value('locale/overrideFlag', False, type=bool)
        if not overrideLocale:
            localeFullName = QtCore.QLocale.system().name()[:2]
        else:
            localeFullName = QtCore.QSettings().value("locale/userLocale", "")

        if QtCore.QFileInfo(userPluginPath).exists():
            translationPath = userPluginPath + '/i18n/pointsinpolygons_' + localeFullName + '.qm'
            self.pluginPath = userPluginPath
        else:
            translationPath = systemPluginPath + '/i18n/pointsinpolygons_' + localeFullName + '.qm'
            self.pluginPath = systemPluginPath

        self.localePath = translationPath
        if QtCore.QFileInfo(self.localePath).exists():
            self.translator = QtCore.QTranslator()
            self.translator.load(self.localePath)
            QgsApplication.installTranslator(self.translator)

        self.pointLayerName = ""
        self.polygonLayerName = ""
        self.fieldName = ""

    def initGui(self):
        self.plPrint("initGui")
        # actionRun = self.addAction("Import", QtGui.QIcon(":/plugins/lesis2sqlite/icons/import.png"))
        # actionRun = self.addAction(self.tr("Recalculate"), None)
        actionRun = self.addAction(
            u"Перерасчитать",
            self.pluginPath + "/icons/points_in_polygons.svg"
        )
        actionRun.triggered.connect(self.run)
        actionSettings = self.addAction(
            u"Настройки",
            self.pluginPath + "/icons/settings.svg",
            False,
            True
        )

        actionSettings.triggered.connect(self.showSettings)

    def unload(self):
        self.delAllActions()

    def showSettings(self):
        settings = QtCore.QSettings()

        dlg = Dialog(
            settings.value("pointsinpolygons_plugin/point_layer_name", ""),
            settings.value("pointsinpolygons_plugin/polygin_layer_name", ""),
            settings.value("pointsinpolygons_plugin/filed_name", ""),
            self._iface.mainWindow()
        )
        res = dlg.exec_()
        if res == Dialog.Accepted:
            # Plugin().plPrint("Save settings")
            plugin_settings = dlg.getSettings()
            settings.setValue("pointsinpolygons_plugin/point_layer_name", plugin_settings[0])
            settings.setValue("pointsinpolygons_plugin/polygin_layer_name", plugin_settings[1])
            settings.setValue("pointsinpolygons_plugin/filed_name", plugin_settings[2])

    def run(self):
        settings = QtCore.QSettings()

        self.pointLayerName = settings.value("pointsinpolygons_plugin/point_layer_name", "")
        self.polygonLayerName = settings.value("pointsinpolygons_plugin/polygin_layer_name", "")
        self.fieldName = settings.value("pointsinpolygons_plugin/filed_name", "")

        Plugin().plPrint("self.pointLayerName: %s" % self.pointLayerName)
        Plugin().plPrint("self.polygonLayerName: %s" % self.polygonLayerName)
        Plugin().plPrint("self.fieldName: %s" % self.fieldName)

        if self.pointLayerName == "" or self.polygonLayerName == "" or self.fieldName == "":
            Plugin().showMessageForUser(
                u"Плагин настроен не корректно. Проверте настройки!",
                QgsMessageBar.CRITICAL,
                0
            )
            return

        pointLayers = QgsMapLayerRegistry.instance().mapLayersByName(self.pointLayerName)
        if len(pointLayers) == 0:
            Plugin().showMessageForUser(
                u"Слой с именем '%s' не найден!" % self.pointLayerName,
                QgsMessageBar.CRITICAL,
                0
            )
            return
        pointLayer = pointLayers[0]

        polygonLayers = QgsMapLayerRegistry.instance().mapLayersByName(self.polygonLayerName)
        if len(polygonLayers) == 0:
            Plugin().showMessageForUser(
                u"Слой с именем '%s' не найден!" % self.polygonLayerName,
                QgsMessageBar.CRITICAL,
                0
            )
            return
        polygonLayer = polygonLayers[0]

        if self.fieldName == "":
            Plugin().showMessageForUser(
                u"Значение поля не задано!",
                QgsMessageBar.CRITICAL,
                0
            )
            return

        progressDlg = QgsBusyIndicatorDialog(u"Подготовка")
        progressDlg.setWindowTitle(u"Идёт расчет")
        worker = Worker(pointLayer, polygonLayer, self.fieldName)
        thread = QtCore.QThread(self._iface.mainWindow())

        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.stoped.connect(thread.quit)
        worker.stoped.connect(worker.deleteLater)
        worker.stoped.connect(thread.deleteLater)
        worker.stoped.connect(progressDlg.close)
        # worker.error.connect(self.showError)
        worker.progressChanged.connect(lambda x, y: progressDlg.setMessage(u"Обработано %d полигонов из %d" % (x, y)))
        thread.start()

        self.thread = thread
        self.worker = worker

        progressDlg.exec_()
