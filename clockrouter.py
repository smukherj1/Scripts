class ClockTree:
	def __init__(self):
		return

	def add_node(self, node_type, x, y, z):
		return

	def add_edge(self, src_type, sx, sy, sz, dest_type, dx, dy, dz):
		print '%s_X%dY%d[%d] -> %s_X%dY%d[%d]'%(
			src_type.upper(),
			sx,
			sy,
			sz,
			dest_type.upper(),
			dx,
			dy,
			dz
		)
		return

	def add_int_edge(self, node_type, x, y, z, from_dir, to_dir, jump_plane):
		print '%s_X%dY%d[%d] %s -> %s'%(
			node_type.upper(),
			x,
			y,
			z,
			from_dir.upper(),
			to_dir.upper()
		)
		return

class ClockRouter:
	def __init__(self, x, y):
		# (x, y) is the sector dimensions of the device
		self.num_planes = 32
		self.x = x
		self.y = y

	def __get_src_dest_dir(self, sx, sy, dx, dy):
		# Can either go "horizonal" or "vertical".
		# Can't do diagonal
		assert sx == dx or sy == dy

		if sx != dx:
			if dx > sx:
				return 'WEST', 'EAST'
			else:
				return 'EAST', 'WEST'
		else:
			if dy > sy:
				return 'SOUTH', 'NORTH'
			else:
				return 'NORTH', 'SOUTH'

	def route_swbox_to_swbox(self, tree, sx, sy, dx, dy, plane):
		assert sx >= 0 and sx < self.x
		assert sy >= 0 and sy < self.y
		assert dx >= 0 and dx < self.x
		assert dy >= 0 and dy < self.y
		assert plane >= 0 and plane < self.num_planes

		# lulwut. Y is da source and destination da same.
		assert sx != dx or sy != dy

		cur_x = sx
		cur_y = sy

		# What direction will x move to reach from sx to dx
		del_x = (dx - sx) / int(abs(dx - sx))
		assert del_x == 1 or del_x == -1

		final_hor_direction = None
		while cur_x != dx:
			next_x = cur_x + del_x
			tree.add_edge('swbox', cur_x, cur_y, plane, 'swbox', next_x, cur_y, plane)
			src_dir, dest_dir = self.__get_src_dest_dir(cur_x, cur_y, next_x, cur_y)
			final_hor_direction = dest_dir
			tree.add_int_edge('swbox', next_x, cur_y, plane, src_dir, dest_dir, jump_plane=False)
			cur_x = next_x

		# What direction will y move to reach from sy to dy
		del_y = (dy - sy) / int(abs(dy - sy))
		assert del_y == 1 or del_y == -1

		while  cur_y != dy:
			next_y = cur_y + del_y
			tree.add_edge('swbox', cur_x, cur_y, plane, 'swbox', cur_x, next_y, plane)
			src_dir, dest_dir = self.__get_src_dest_dir(cur_x, cur_y, cur_x, next_y)
			if final_hor_direction != None:
				src_dir = final_hor_direction
				final_hor_direction = None
			tree.add_int_edge('swbox', cur_x, next_y, plane, src_dir, dest_dir, jump_plane=False)
			cur_y = next_y

if __name__ == '__main__':
	tree = ClockTree()
	router = ClockRouter(9, 11)

	router.route_swbox_to_swbox(tree, 8, 8, 0, 0, 0)
