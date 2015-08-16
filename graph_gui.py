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
		self.__highlight = False
		self.__node = None

	def place(self, node):
		self.__node = node
		self.update()

	def unplace(self):
		n = self.__node
		self.__node = None
		self.update()
		return n

	def mouseDoubleClickEvent(self, event):
		if self.__node:
			self.parent().showNode(self.__node.gid)
		self.update()

	def highlight(self):
		self.__highlight = True
		if self.__node:
			self.parent().highlightNode(self.__node)
		self.update()

	def unhighlight(self):
		self.__highlight = False
		if self.__node:
			self.parent().unhighlightNode(self.__node)
		self.update()

	def enterEvent(self, event):
		self.highlight()

	def leaveEvent(self, event):
		self.unhighlight()

	def paintEvent(self, event):
		self.adjustSize()
		qp = QtGui.QPainter()
		qp.begin(self)
		if self.__highlight and self.__node:
			qp.fillRect(event.rect(), QtCore.Qt.red)
		else:
			qp.fillRect(event.rect(), self.parent().getColor(self.__node))
		if self.__node:
			p = QtGui.QPen(QtCore.Qt.black)
			p.setWidth(4)
			qp.setPen(p)
			qp.drawRect(event.rect())
		qp.end()

class DrawableArea(QtGui.QWidget):
	def __init__(self, device, infoPanel, faninInfoPanel, fanoutInfoPanel, parent=None):
		super(DrawableArea, self).__init__(parent=parent)
		self.__device = device
		self.__infoPanel = infoPanel
		self.__faninInfoPanel = faninInfoPanel
		self.__fanoutInfoPanel = fanoutInfoPanel
		self.__widgetGrid = []
		self.__nx = -1
		self.__ny = -1
		self.__curNode = None
		self.__nodeToPlacementMap = {}
		self.__highlightedWidget = None
		# The color to use when clearing this widget. Use the default color
		# of the widget for this purpose
		self.__clearColor = self.palette().color(QtGui.QPalette.Background)

		self.__nodeStack = []
		self.__faninInfoPanel.itemClicked.connect(self.listItemSelect)
		self.__fanoutInfoPanel.itemClicked.connect(self.listItemSelect)
		self.__faninInfoPanel.itemDoubleClicked.connect(self.listItemDoubleClick)
		self.__fanoutInfoPanel.itemDoubleClicked.connect(self.listItemDoubleClick)

		self.setMouseTracking(True)

	def gridToActual(self, x, y):
		return (x * self.__dx + self.__p, 
			y * self.__dy + self.__p, 
			self.__dx - 2 * self.__p, 
			self.__dy - 2 * self.__p)

	def freeGrid(self, nx, ny):
		if not self.__widgetGrid:
			return
		for ix in xrange(nx):
			for iy in xrange(ny):
				w = self.__widgetGrid[ix][iy]
				w.hide()
				del w
		return

	def createGrid(self):
		self.__widgetGrid = []
		for ix in xrange(self.__nx):
			self.__widgetGrid.append([])
			for iy in xrange(self.__ny):
				self.__widgetGrid[ix].append(NodeWidget(self))
				x, y, w, h = self.gridToActual(ix, iy)
				self.__widgetGrid[ix][iy].resize(w, h)
				self.__widgetGrid[ix][iy].move(x, y)
				self.__widgetGrid[ix][iy].show()

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
				self.__widgetGrid[ix][iy].unplace()

	def getColor(self, node):
		if not node:
			return self.__clearColor
		elif node.gid in self.__curNode.fanins and node.gid in self.__curNode.fanouts:
			return QtCore.Qt.green
		elif node.gid in self.__curNode.fanins:
			return QtCore.Qt.yellow
		elif node.gid in self.__curNode.fanouts:
			return QtCore.Qt.cyan
		else:
			raise RuntimeError('%s was neither a fanin nor a fanout of %s'%(node, self.__curNode))

	def showPreviousNode(self):
		if not self.__nodeStack:
			return
		last_gid = self.__nodeStack.pop()
		# Clear the current node or else showNode will add it back
		# to the stack
		self.__curNode = None
		self.showNode(last_gid)
		return

	def showNode(self, gid):
		node = self.__device.getNodeByGID(gid)
		if self.__curNode:
			self.__nodeStack.append(self.__curNode.gid)
		self.__curNode = node
		faninList = [self.__device.getNodeByGID(fanin_gid) for fanin_gid in node.fanins]
		fanoutList = [self.__device.getNodeByGID(fanout_gid) for fanout_gid in node.fanouts]
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
			self.__widgetGrid[x][y].place(node)
		self.__faninInfoPanel.clear()
		self.__fanoutInfoPanel.clear()
		self.__infoPanel.clear()
		self.__infoPanel.addItem('Traversing %s'%str(node))
		self.__infoPanel.insertItem(1, "")
		self.__faninInfoPanel.addItem('Fanins (%d):-'%len(faninList))
		for node in faninList:
			self.__faninInfoPanel.addItem('%s gid:%d fanouts:%d fanins:%d'%(str(node), node.gid, len(node.fanouts), len(node.fanins)))
		self.__fanoutInfoPanel.addItem('Fanouts (%d):-'%len(fanoutList))
		for node in fanoutList:
			self.__fanoutInfoPanel.addItem('%s gid:%d fanouts:%d fanins:%d'%(str(node), node.gid, len(node.fanouts), len(node.fanins)))
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
		if self.__highlightedWidget:
			self.__highlightedWidget.unhighlight()
		self.__widgetGrid[x][y].highlight()
		self.__highlightedWidget = self.__widgetGrid[x][y]
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
		if self.__highlightedWidget:
			w = self.__highlightedWidget
			self.__highlightedWidget = None
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

		self.__infoPanel.item(1).setText(str(node) + descr_text)
		return

	def unhighlightNode(self, node):
		if self.__highlightedWidget:
			w = self.__highlightedWidget
			self.__highlightedWidget = None
			w.unhighlight()
		self.__infoPanel.item(1).setText("")
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
		self.__main_hbox = QtGui.QHBoxLayout()
		
		self.__panelVBox = QtGui.QVBoxLayout()
		self.__infoPanel = QtGui.QListWidget()
		self.__faninInfoPanel = QtGui.QListWidget()
		self.__fanoutInfoPanel = QtGui.QListWidget()
		self.__goButton = QtGui.QPushButton('Start')
		self.__backButton = QtGui.QPushButton('Back')
		self.__goButton.clicked.connect(self.start)
		self.__panelVBox.addWidget(self.__infoPanel)
		self.__panelVBox.addWidget(self.__faninInfoPanel)
		self.__panelVBox.addWidget(self.__fanoutInfoPanel)
		self.__panelVBox.addWidget(self.__backButton)
		self.__panelVBox.addWidget(self.__goButton)

		self.__daw = DrawableArea(device, self.__infoPanel, self.__faninInfoPanel, self.__fanoutInfoPanel, self)
		self.__main_hbox.addWidget(self.__daw)
		self.__backButton.clicked.connect(self.__daw.showPreviousNode)
		self.__main_hbox.addLayout(self.__panelVBox)
		self.setLayout(self.__main_hbox)
		self.__main_hbox.setStretch(0, 4)
		self.__main_hbox.setStretch(1, 1)
		self.__panelVBox.setStretch(0, 1)
		self.__panelVBox.setStretch(1, 4)
		self.__panelVBox.setStretch(2, 4)

	def start(self):
		self.__daw.showNode(0)

def main():
	app = QtGui.QApplication(sys.argv)
	g = GraphGui(DeviceInterface())
	g.showMaximized()
	return app.exec_()

main()