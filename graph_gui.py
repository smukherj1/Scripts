from PyQt4 import QtGui
from PyQt4 import QtCore
import sys
import json
from layout import Node
from layout import LayoutEngine

class DeviceInterface:
	def __init__(self):
		self.__gid_to_node_map = {}
		data = json.load(open('d.json'))
		for jsonObj in data:
			node = Node(**jsonObj)
			self.__gid_to_node_map[node.gid] = node

	def getNodeByGID(self, gid):
		return self.__gid_to_node_map[gid]

class NodeWidget(QtGui.QWidget):
	def __init__(self, parent=None):
		super(NodeWidget, self).__init__(parent=parent)
		self.setMouseTracking(True)
		self._highlight = False

	def enterEvent(self, event):
		self._highlight = True
		self.update()

	def leaveEvent(self, event):
		self._highlight = False
		self.update()

	def paintEvent(self, event):
		self.adjustSize()
		qp = QtGui.QPainter()
		qp.begin(self)
		if self._highlight:
			qp.fillRect(event.rect(), QtCore.Qt.red)
		else:
			qp.fillRect(event.rect(), QtCore.Qt.yellow)
		p = QtGui.QPen(QtCore.Qt.black)
		p.setWidth(6)
		qp.setPen(p)
		qp.drawRect(event.rect())
		qp.end()

class DrawableArea(QtGui.QWidget):
	def __init__(self, device, infoPanel, faninInfoPanel, fanoutInfoPanel, parent=None):
		super(DrawableArea, self).__init__(parent=parent)
		self._infoPanel = infoPanel
		self._faninInfoPanel = faninInfoPanel
		self._fanoutInfoPanel = fanoutInfoPanel
		self._widgetGrid = []
		self.__nx = -1
		self.__ny = -1

		self.setMouseTracking(True)

	def gridToActual(self, x, y):
		return (x * self.__dx + self.__p, 
			y * self.__dy + self.__p, 
			self.__dx - 2 * self.__p, 
			self.__dy - 2 * self.__p)

	def freeGrid(self, nx, ny):
		if not self._widgetGrid:
			return
		for ix in xrange(nx):
			for iy in xrange(ny):
				w = self._widgetGrid[ix][iy]
				w.hide()
				del w
		return

	def createGrid(self):
		self._widgetGrid = []
		for ix in xrange(self.__nx):
			self._widgetGrid.append([])
			for iy in xrange(self.__ny):
				self._widgetGrid[ix].append(NodeWidget(self))
				x, y, w, h = self.gridToActual(ix, iy)
				self._widgetGrid[ix][iy].resize(w, h)
				self._widgetGrid[ix][iy].move(x, y)
				self._widgetGrid[ix][iy].show()

	def adjustSize(self):
		# Block width
		self.__dx = 80
		# Block height
		self.__dy = 100
		# Padding
		self.__p = 2
		self.__old_nx = self.__nx
		self.__old_ny = self.__ny
		self.__nx = self.width() / self.__dx
		self.__ny = self.height() / self.__dy
		#print self.__nx, self.__ny, self.width(), self.height(), self.__dx, self.__dy

		if self.__old_nx != self.__nx or self.__old_ny != self.__ny:
			self.freeGrid(self.__old_nx, self.__old_ny)
			self.createGrid()
		return

	def paintEvent(self, event):
		self.adjustSize()
		qp = QtGui.QPainter()
		qp.begin(self)
		#qp.fillRect(event.rect(), QtCore.Qt.red)
		qp.end()

class GraphGui(QtGui.QWidget):
	def __init__(self, device, parent=None):
		super(GraphGui, self).__init__(parent=parent)
		self._main_hbox = QtGui.QHBoxLayout()
		
		self._panelVBox = QtGui.QVBoxLayout()
		self._infoPanel = QtGui.QListWidget()
		self._faninInfoPanel = QtGui.QListWidget()
		self._fanoutInfoPanel = QtGui.QListWidget()
		self._panelVBox.addWidget(self._infoPanel)
		self._panelVBox.addWidget(self._faninInfoPanel)
		self._panelVBox.addWidget(self._fanoutInfoPanel)

		self._daw = DrawableArea(device, self._infoPanel, self._faninInfoPanel, self._fanoutInfoPanel, self)
		self._main_hbox.addWidget(self._daw)
		self._main_hbox.addLayout(self._panelVBox)
		self.setLayout(self._main_hbox)
		self._main_hbox.setStretch(0, 4)
		self._main_hbox.setStretch(1, 1)
		self._panelVBox.setStretch(0, 1)
		self._panelVBox.setStretch(1, 4)
		self._panelVBox.setStretch(2, 4)

def main():
	app = QtGui.QApplication(sys.argv)
	g = GraphGui(DeviceInterface())
	g.showMaximized()
	return app.exec_()

main()