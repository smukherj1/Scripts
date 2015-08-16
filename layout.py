import time

class Node(object):
	def __init__(self, gid, node_type, x, y, z=0, i=0, fanouts=[], fanins=[]):
		self.__gid = int(gid)
		self.__type = str(node_type)
		self.__x = int(x)
		self.__y = int(y)
		self.__z = int(z)
		self.__i = int(i)
		self.__fanouts = fanouts
		self.__fanins = fanins

	@property
	def gid(self):
		return self.__gid

	@property
	def type(self):
		return self.__type

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

	@property
	def z(self):
		return self.__z

	@property
	def i(self):
		return self.__i

	@property
	def fanins(self):
		return [i for i in self.__fanins]

	@fanins.setter
	def fanins(self, fanins):
		self.__fanins = [i for i in fanins]

	@property
	def fanouts(self):
		return [i for i in self.__fanouts]

	@fanouts.setter
	def fanouts(self, fanouts):
		self.__fanouts = [i for i in fanouts]

	def toJSON(self):
		JSONstr = '{'
		JSONstr += '"gid": %d,'%self.gid
		JSONstr += ' "node_type": "%s",'%str(self.type)
		JSONstr += ' "x": %d,'%self.x
		JSONstr += ' "y": %d,'%self.y
		JSONstr += ' "z": %d,'%self.z
		JSONstr += ' "i": %d,'%self.i
		JSONstr += ' "fanins": %s,'%str(self.fanins)
		JSONstr += ' "fanouts": %s'%str(self.fanouts)
		JSONstr += '}'
		return JSONstr

	def __repr__(self):
		return '%s_X%d_Y%d_N%d_I%d'%(self.type, self.x, self.y, self.z, self.i)

	def __str__(self):
		return '%s_X%d_Y%d_N%d_I%d'%(self.type, self.x, self.y, self.z, self.i)



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

	def getNodeWrapperDistance(self, nw):
		x, y = self.getNodeWrapperVector(nw)
		return (x ** 2) + (y ** 2)

	def getNodeWrapperVector(self, nw):
		return ((nw.node.x - self.__centerNode.x) * 2, (nw.node.y - self.__centerNode.y) * 2)

	def getLocationVector(self, x, y):
		return (x - (self.__nx / 2), y - (self.__ny / 2))

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
			nw.loc = bestLoc
		return bestLoc != None

	def run(self):
		start_time = time.time()
		for nwrapper in sorted(self.__nodeWrapperList, key = lambda nw: self.getNodeWrapperDistance(nw), reverse=True):
			self.place(nwrapper)
		#print 'LayoutEngine took %.0f s'%(time.time() - start_time)
		return

	def placement(self):
		return self.__nodeWrapperList

	def debug(self):
		for nwrapper in self.__nodeWrapperList:
			print nwrapper


if __name__ == '__main__':
	nodeList = [ Node(0, 'Top-Left', 0, 0),
	Node(1, 'Top', 0, 1),
	Node(2, 'Top-Right', 0, 2),
	Node(3, 'Left', 1, 0),
	Node(4, 'Right', 1, 2),
	Node(5, 'Bottom-Left', 2, 0),
	Node(6, 'Bottom', 2, 1),
	Node(7, 'Bottom-Right', 2, 2)
	]

	le = LayoutEngine(nodeList, Node(8, 'Center', 1, 1), 3, 3)
	le.run()
	le.debug()