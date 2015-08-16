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
		self._node = None

	def place(self, node):
		self._node = node
		self.update()

	def unplace(self):
		n = self._node
		self._node = None
		self.update()
		return n

	def mouseDoubleClickEvent(self, event):
		if self._node:
			self.parent().showNode(self._node.gid)
		self.update()

	def highlight(self):
		self._highlight = True
		if self._node:
			self.parent().highlightNode(self._node)
		self.update()

	def unhighlight(self):
		self._highlight = False
		if self._node:
			self.parent().unhighlightNode(self._node)
		self.update()

	def enterEvent(self, event):
		self.highlight()

	def leaveEvent(self, event):
		self.unhighlight()

	def paintEvent(self, event):
		self.adjustSize()
		qp = QtGui.QPainter()
		qp.begin(self)
		if self._highlight and self._node:
			qp.fillRect(event.rect(), QtCore.Qt.red)
		else:
			qp.fillRect(event.rect(), self.parent().getColor(self._node))
		if self._node:
			p = QtGui.QPen(QtCore.Qt.black)
			p.setWidth(4)
			qp.setPen(p)
			qp.drawRect(event.rect())
		qp.end()

class DrawableArea(QtGui.QWidget):
	def __init__(self, device, infoPanel, faninInfoPanel, fanoutInfoPanel, parent=None):
		super(DrawableArea, self).__init__(parent=parent)
		self._device = device
		self._infoPanel = infoPanel
		self._faninInfoPanel = faninInfoPanel
		self._fanoutInfoPanel = fanoutInfoPanel
		self._widgetGrid = []
		self.__nx = -1
		self.__ny = -1
		self.__curNode = None
		self.__nodeToPlacementMap = {}
		self._highlightedWidget = None
		# The color to use when clearing this widget. Use the default color
		# of the widget for this purpose
		self._clearColor = self.palette().color(QtGui.QPalette.Background)

		self._nodeStack = []
		self._faninInfoPanel.itemClicked.connect(self.listItemSelect)
		self._fanoutInfoPanel.itemClicked.connect(self.listItemSelect)
		self._faninInfoPanel.itemDoubleClicked.connect(self.listItemDoubleClick)
		self._fanoutInfoPanel.itemDoubleClicked.connect(self.listItemDoubleClick)

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

	def unplaceAllNodes(self):
		for ix in xrange(self.__nx):
			for iy in xrange(self.__ny):
				self._widgetGrid[ix][iy].unplace()

	def getColor(self, node):
		if not node:
			return self._clearColor
		elif node.gid in self.__curNode.fanins and node.gid in self.__curNode.fanouts:
			return QtCore.Qt.green
		elif node.gid in self.__curNode.fanins:
			return QtCore.Qt.yellow
		elif node.gid in self.__curNode.fanouts:
			return QtCore.Qt.cyan
		else:
			raise RuntimeError('%s was neither a fanin nor a fanout of %s'%(node, self.__curNode))

	def showPreviousNode(self):
		print self._nodeStack
		if not self._nodeStack:
			return
		last_gid = self._nodeStack.pop()
		# Clear the current node or else showNode will add it back
		# to the stack
		self.__curNode = None
		self.showNode(last_gid)
		return

	def showNode(self, gid):
		node = self._device.getNodeByGID(gid)
		if self.__curNode:
			self._nodeStack.append(self.__curNode.gid)
		self.__curNode = node
		faninList = [self._device.getNodeByGID(fanin_gid) for fanin_gid in node.fanins]
		fanoutList = [self._device.getNodeByGID(fanout_gid) for fanout_gid in node.fanouts]
		nodeList = list(set(faninList) | set(fanoutList))
		layoutEngine = LayoutEngine(nodeList, node, self.__ny, self.__nx)
		layoutEngine.run()
		placement = layoutEngine.placement()
		self.unplaceAllNodes()
		self.__nodeToPlacementMap.clear()
		for nodeWrapper in placement:
			node = nodeWrapper.node
			x, y = nodeWrapper.loc
			self.__nodeToPlacementMap[node.gid] = (x, y)
			self._widgetGrid[x][y].place(node)
		self._faninInfoPanel.clear()
		self._fanoutInfoPanel.clear()
		self._infoPanel.clear()
		self._infoPanel.addItem('Traversing %s'%str(node))
		self._infoPanel.insertItem(1, "")
		self._faninInfoPanel.addItem('Fanins (%d):-'%len(faninList))
		for node in faninList:
			self._faninInfoPanel.addItem('%s gid:%d fanouts:%d fanins:%d'%(str(node), node.gid, len(node.fanouts), len(node.fanins)))
		self._fanoutInfoPanel.addItem('Fanouts (%d):-'%len(fanoutList))
		for node in fanoutList:
			self._fanoutInfoPanel.addItem('%s gid:%d fanouts:%d fanins:%d'%(str(node), node.gid, len(node.fanouts), len(node.fanins)))
		return

	def parseNodeGIDFromListItem(self, text):
		split_text = text.split()
		if len(split_text) != 4:
			return
		gid_text = split_text[1]
		gid_split_text = gid_text.split(':')
		if len(gid_split_text) != 2:
			return
		if not gid_split_text[1].isdigit():
			return
		return int(gid_split_text[1])

	def listItemSelect(self, listItem):
		listItemText = str(listItem.text())
		gid = self.parseNodeGIDFromListItem(listItemText)
		if not gid:
			return
		x, y = self.__nodeToPlacementMap[gid]
		if self._highlightedWidget:
			self._highlightedWidget.unhighlight()
		self._widgetGrid[x][y].highlight()
		self._highlightedWidget = self._widgetGrid[x][y]
		return

	def listItemDoubleClick(self, listItem):
		listItemText = str(listItem.text())
		gid = self.parseNodeGIDFromListItem(listItemText)
		if not gid:
			return
		self.showNode(gid)
		return

	############### Callbacks for children widgets #################
	def highlightNode(self, node):
		if self._highlightedWidget:
			w = self._highlightedWidget
			self._highlightedWidget = None
			w.unhighlight()

		descr_text = ""
		is_fanin = node.gid in self.__curNode.fanins
		is_fanout = node.gid in self.__curNode.fanouts
		if is_fanin and is_fanout:
			descr_text = " is a fanin and fanout"
		elif is_fanin:
			descr_text = " is a fanin"
		elif is_fanout:
			descr_text = " is a fanout"

		self._infoPanel.item(1).setText(str(node) + descr_text)
		return

	def unhighlightNode(self, node):
		if self._highlightedWidget:
			w = self._highlightedWidget
			self._highlightedWidget = None
			w.unhighlight()
		self._infoPanel.item(1).setText("")
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
		self._goButton = QtGui.QPushButton('Start')
		self._backButton = QtGui.QPushButton('Back')
		self._goButton.clicked.connect(self.start)
		self._panelVBox.addWidget(self._infoPanel)
		self._panelVBox.addWidget(self._faninInfoPanel)
		self._panelVBox.addWidget(self._fanoutInfoPanel)
		self._panelVBox.addWidget(self._backButton)
		self._panelVBox.addWidget(self._goButton)

		self._daw = DrawableArea(device, self._infoPanel, self._faninInfoPanel, self._fanoutInfoPanel, self)
		self._main_hbox.addWidget(self._daw)
		self._backButton.clicked.connect(self._daw.showPreviousNode)
		self._main_hbox.addLayout(self._panelVBox)
		self.setLayout(self._main_hbox)
		self._main_hbox.setStretch(0, 4)
		self._main_hbox.setStretch(1, 1)
		self._panelVBox.setStretch(0, 1)
		self._panelVBox.setStretch(1, 4)
		self._panelVBox.setStretch(2, 4)

	def start(self):
		self._daw.showNode(0)

def main():
	app = QtGui.QApplication(sys.argv)
	g = GraphGui(DeviceInterface())
	g.showMaximized()
	return app.exec_()

main()