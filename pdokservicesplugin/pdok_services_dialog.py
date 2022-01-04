# -*- coding: utf-8 -*-

import os

from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QDialog,
)

from qgis.PyQt import uic


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'pdok_services_dialog.ui'))

class PdokServicesDialog(QDialog, FORM_CLASS):

    def __init__(self, plugin, parent=None):

        super(PdokServicesDialog, self).__init__(parent)
        self.setupUi(self)

        self.plugin = plugin

        # only select one row at a time:
        self.layers_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.layers_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.layers_table.setAutoScroll(False)

        # select whole row if an item is clicked
        self.geocoderResultView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.geocoderResultView.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.tabs = self.tabWidget  # TODO: why changing this name??

        # close button
        self.buttonBox.rejected.connect(self.reject)
