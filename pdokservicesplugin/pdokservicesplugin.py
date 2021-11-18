# -*- coding: utf-8 -*-

import os

from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon

from qgis.core import QgsApplication

from .locator_filter.pdoklocatieserverfilter import PDOKLocatieserverLocatorFilter
from .pdok_services_dialog import PdokServicesDialog
from .processing_provider.provider import Provider




class PdokServicesPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        # services dialog
        self.services_dlg = PdokServicesDialog(self, parent=self.iface.mainWindow())

        # locator filter
        self.filter = PDOKLocatieserverLocatorFilter(self.iface)
        self.iface.registerLocatorFilter(self.filter)

        self.provider = None


    def initGui(self):
        add_service_icon = QIcon(os.path.join(self.plugin_dir, 'img', 'icon_add_service.svg'))
        self.add_service_action = QAction(add_service_icon, 'Voeg PDOK-kaartlaag toe...', self.iface.mainWindow())
        self.add_service_action.triggered.connect(self.show_add_service_dlg)

        self.toolbar = self.iface.addToolBar("PDOK Services Plugin")
        self.toolbar.addAction(self.add_service_action)

        self.provider = Provider()
        QgsApplication.processingRegistry().addProvider(self.provider)


    def unload(self):
        self.iface.deregisterLocatorFilter(self.filter)
        QgsApplication.processingRegistry().removeProvider(self.provider)

        self.add_service_action.triggered.disconnect(self.show_add_service_dlg)
        self.toolbar.removeAction(self.add_service_action)
        del self.add_service_action

        del self.toolbar




    def show_add_service_dlg(self):
        #QMessageBox.information(None, 'PDOK Services Plugin', 'Dummy text')
        self.services_dlg.show()
