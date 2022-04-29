# -*- coding: utf-8 -*-

import os

from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QAction,
)
from qgis.PyQt.QtGui import (
    QIcon,
    QStandardItem,
    QStandardItemModel,
)
from qgis.PyQt.QtCore import (
    Qt,
    QSortFilterProxyModel,
)

import json

from qgis.core import QgsApplication

from .locator_filter.pdoklocatieserverfilter import PDOKLocatieserverLocatorFilter
from .pdok_services_dialog import PdokServicesDialog
from .processing_provider.provider import Provider
from .layer_registry import LayerRegistry

import logging
from . import LOGGER_NAME

log = logging.getLogger(LOGGER_NAME)


class PdokServicesPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        # services dialog
        self.dlg = PdokServicesDialog(self, parent=self.iface.mainWindow())

        # locator filter
        self.filter = PDOKLocatieserverLocatorFilter(self.iface)
        self.iface.registerLocatorFilter(self.filter)

        self.provider = None
        self.layer_registry = None

    def initGui(self):
        add_layer_icon = QIcon(
            os.path.join(self.plugin_dir, "img", "icon_add_service.svg")
        )
        self.add_layer_action = QAction(
            add_layer_icon, "Voeg PDOK-kaartlaag toe...", self.iface.mainWindow()
        )
        self.add_layer_action.triggered.connect(self.show_add_service_dlg)

        self.toolbar = self.iface.addToolBar("PDOK Services Plugin")
        self.toolbar.setObjectName(
            "PDOK Services Plugin"
        )  # without this Qt complains" "Qt: QMainWindow::saveState(): 'objectName' not set for QToolBar 0x560b3b88f5a0 'PDOK Services Plugin'"
        self.toolbar.addAction(self.add_layer_action)

        self.dlg.search_layer_edit.textEdited.connect(self.filter_layers)
        self.dlg.search_layer_edit.setPlaceholderText(
            "woord uit laagnaam, type of service "
        )

        self.provider = Provider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        self.iface.deregisterLocatorFilter(self.filter)
        QgsApplication.processingRegistry().removeProvider(self.provider)

        self.add_layer_action.triggered.disconnect(self.show_add_service_dlg)
        self.toolbar.removeAction(self.add_layer_action)

        self.dlg.search_layer_edit.textEdited.disconnect(self.filter_layers)

        del self.add_layer_action

        del self.toolbar

    def add_layer_row(self, serviceLayer):
        # you can attache different "data's" to to an QStandarditem
        # default one is the visible one:
        item_type = QStandardItem("%s" % (serviceLayer["type"].upper()))
        # userrole is a free form one:
        # only attach the data to the first item
        # service layer = a dict/object with all props of the layer
        item_type.setData(serviceLayer, Qt.UserRole)
        item_type.setToolTip(
            "%s - %s" % (serviceLayer["type"].upper(), serviceLayer["title"])
        )
        # only wms services have styles (sometimes)
        layer_name = serviceLayer["title"]
        if "style" in serviceLayer:
            item_layer_name = QStandardItem(
                "%s [%s]" % (serviceLayer["title"], serviceLayer["style"])
            )
            layer_name = "%s [%s]" % (serviceLayer["title"], serviceLayer["style"])
        else:
            item_layer_name = QStandardItem("%s" % (serviceLayer["title"]))
        item_layer_name.setToolTip(
            "%s - %s" % (serviceLayer["type"].upper(), serviceLayer["servicetitle"])
        )
        item_service_title = QStandardItem("%s" % (serviceLayer["servicetitle"]))
        item_service_title.setToolTip(
            "%s - %s" % (serviceLayer["type"].upper(), serviceLayer["title"])
        )
        # itemFilter is the item used to search filter in. That is why layername is a combi of layername + filter here
        #        item_filter = QStandardItem("%s %s %s %s" % (serviceLayer["type"], layer_name, serviceLayer["servicetitle"], serviceLayer["abstract"]) )
        #        self.table_model.appendRow([item_layer_name, item_type, item_service_title, item_filter])
        self.table_model.appendRow([item_layer_name, item_type, item_service_title])

    def filter_layers(self, text):
        log.debug(f"Zoek naar: {text}")
        QgsApplication.setOverrideCursor(Qt.WaitCursor)
        if len(text) == 0:
            layers = self.layer_registry.layers
        elif len(text) == 1:
            layers = []
        else:
            layers = self.layer_registry.query(text)
        QgsApplication.restoreOverrideCursor()
        self.fill_layer_table(layers)

    def fill_layer_table(self, layers):
        self.table_model = QStandardItemModel()
        self.dlg.layers_table.setModel(self.table_model)

        #        self.table_proxy_model = QSortFilterProxyModel()
        #        self.table_proxy_model.setSourceModel(self.table_model)
        #        self.table_proxy_model.setFilterKeyColumn(3)
        #        self.dlg.layers_table.setModel(self.table_proxy_model)
        self.dlg.layers_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # self.geocoderProxyModel = QSortFilterProxyModel()
        # self.geocoderSourceModel = QStandardItemModel()
        # self.geocoderProxyModel.setSourceModel(self.geocoderSourceModel)
        # self.geocoderProxyModel.setFilterKeyColumn(0)
        # self.dlg.geocoderResultView.setModel(self.geocoderProxyModel)
        # self.dlg.geocoderResultView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # {"services":[
        #   {"naam":"WMS NHI","url":"http://geodata.nationaalgeoregister.nl/nhi/ows","layers":["dmlinks","dmnodes"],"type":"wms"},
        #   {"naam":"WMS NHI","url":"http://geodata.nationaalgeoregister.nl/nhi/ows","layers":["dmlinks","dmnodes"],"type":"wms"}
        # ]}
        #
        for layer_dict in layers:
            # service[layer] was an array
            if isinstance(layer_dict["layers"], str):
                self.add_layer_row(layer_dict)

        # self.dlg.layers_table.selectionModel().selectionChanged.connect(self.showService)
        # self.dlg.layers_table.doubleClicked.connect(lambda: self.loadService(None)) # Using lambda here to prevent sending signal parameters to the loadService() function
        #
        # self.dlg.layers_table.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.dlg.layers_table.customContextMenuRequested.connect(self.make_favourite)
        #
        # # actually I want to load a service when doubleclicked on header
        # # but as I cannot get this to work, let's disable clicking it then
        self.dlg.layers_table.verticalHeader().setSectionsClickable(False)
        self.dlg.layers_table.horizontalHeader().setSectionsClickable(False)
        #
        # #self.dlg.geocoderResultView.doubleClicked.connect(self.zoomToAddress)
        # self.dlg.geocoderResultView.selectionModel().selectionChanged.connect(self.zoomToAddress)
        #
        # self.layers_loaded_from_json = True;
        # but: hide the itemFilter column

    def show_add_service_dlg(self):

        if self.layer_registry is None:
            self.layer_registry = LayerRegistry()
            self.layer_registry.load_layer_json(
                os.path.join(self.plugin_dir, "pdok.json")
            )
            self.filter_layers("")

        # TODO? kan dit ook niet eenmalig?
        self.dlg.layers_table.hideColumn(3)
        self.table_model.setHeaderData(2, Qt.Horizontal, "Service")
        self.table_model.setHeaderData(1, Qt.Horizontal, "Type")
        self.table_model.setHeaderData(0, Qt.Horizontal, "Laagnaam [style]")
        self.table_model.horizontalHeaderItem(2).setTextAlignment(Qt.AlignLeft)
        self.table_model.horizontalHeaderItem(1).setTextAlignment(Qt.AlignLeft)
        self.table_model.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
        # self.dlg.servicesView.verticalHeader().hide()
        # self.dlg.servicesView.resizeColumnsToContents()
        self.dlg.layers_table.setColumnWidth(
            0, 300
        )  # set name to 300px (there are some huge layernames)
        self.dlg.layers_table.horizontalHeader().setStretchLastSection(True)

        self.dlg.show()
