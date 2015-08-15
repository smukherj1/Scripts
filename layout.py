
class Node(object):
	def __init__(self, name, x, y):
		self.__name = str(name)
		self.__x = int(x)
		self.__y = int(y)

	@property
	def name(self):
		return self.__name

	@property
	def x(self):
		return self.__x

	@x.setter
	def x(self, x):
		self.__x = int(x)

	@property
	def y(self):
		return self.__y

	@y.setter
	def y(self, y):
		self.__y = int(y)

	def __repr__(self):
		return '%s_X%d_Y%d'%(self.name(), self.x(), self.y())

	def __str__(self):
		return '%s_X%d_Y%d'%(self.name, self.x, self.y)



class NodeWrapper(object):
	def __init__(self, node):
		self.__node = node
		self.__loc = (-1, -1)

	@property
	def node(self):
		return self.__node

	@property
	def loc(self):
		return (int(self.__loc[0]), int(self.__loc[1]))

	@loc.setter
	def loc(self, loc):
		self.__loc = (int(loc[0]), int(loc[1]))

	def __repr__(self):
		return '<%s, (%d, %d)>'%(str(self.__node), self.loc[0], self.loc[1])

	def __str__(self):
		return '<%s, (%d, %d)>'%(str(self.__node), self.loc[0], self.loc[1])



class LayoutEngine:
	def __init__(self, 
		nodeList, 
		centerNode,
		layoutRows,
		layoutCols):
		'''
		Each node object in nodeList and the centerNode must have 'x' and 'y' properties
		'''
		self.__nodeWrapperList = [NodeWrapper(n) for n in nodeList]
		self.__centerNode = centerNode
		self.__ny = int(layoutRows)
		self.__nx = int(layoutCols)
		self.__grid = []
		for i in xrange(self.__nx):
			self.__grid.append([])
			for j in xrange(self.__ny):
				self.__grid[i].append(None)

	def getNodeWrapperVector(self, nw):
		return (nw.node.x - self.__centerNode.x, nw.node.y - self.__centerNode.y)

	def getLocationVector(self, x, y):
		return (x - self.__centerNode.x, y - self.__centerNode.y)

	def vectorDifferenceCost(self, v1, v2):
		return (v1[0] - v2[0]) ** 2 +  (v1[1] - v2[1]) ** 2

	def place(self, nw):
		nv = self.getNodeWrapperVector(nw)
		minCost = None
		bestLoc = None
		for ix in xrange(self.__nx):
			for iy in xrange(self.__ny):
				if self.__grid[ix][iy]:
					continue
				lv = self.getLocationVector(ix, iy)
				cost = self.vectorDifferenceCost(nv, lv)
				#print nw.node, 'at', str((ix, iy)), 'nv=', str(nv), 'lv=', lv, 'cost=', cost
				if minCost == None or cost < minCost:
					minCost = cost
					bestLoc = (ix, iy)

		if bestLoc:
			self.__grid[bestLoc[0]][bestLoc[1]] = nw
			#import pdb; pdb.set_trace()
			nw.loc = bestLoc
		return bestLoc != None

	def run(self):
		for nwrapper in self.__nodeWrapperList:
			self.place(nwrapper)
		return

	def debug(self):
		for nwrapper in self.__nodeWrapperList:
			print nwrapper


if __name__ == '__main__':
	nodeList = [ Node('Top-Left', 0, 0),
	Node('Top', 0, 1),
	Node('Top-Right', 0, 2),
	Node('Left', 1, 0),
	Node('Right', 1, 2),
	Node('Bottom-Left', 2, 0),
	Node('Bottom', 2, 1),
	Node('Bottom-Right', 2, 2)
	]

	le = LayoutEngine(nodeList, Node('Center', 1, 1), 3, 3)
	le.run()
	le.debug()