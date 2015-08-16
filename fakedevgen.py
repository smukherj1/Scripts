from layout import Node

nx = 10
ny = 10
last_gid = -1

grid = []
for ix in xrange(nx):
	grid.append([])
	for iy in xrange(ny):
		grid[ix].append([])

def get_elem_of_type(x, y, node_type):
	for n in grid[x][y]:
		if n.type == node_type:
			return n
	return

def create_elems_of_type(node_type, z=0, i=0):
	global last_gid
	for ix in xrange(nx):
		for iy in xrange(ny):
			grid[ix][iy].append(Node(last_gid + 1, node_type, ix, iy, z, i))
			last_gid += 1

def connect(src, dest):
	if not src or not dest:
		return
	src_fanouts = src.fanouts
	dest_fanins = dest.fanins
	src_fanouts.append(dest.gid)
	dest_fanins.append(src.gid)
	src.fanouts = src_fanouts
	dest.fanins = dest_fanins
	return

def connect_neighbours(src_type, dest_type, offset=1):
	for ix in xrange(nx):
		for iy in xrange(ny):
			src = get_elem_of_type(ix, iy, src_type)
			if ix > (offset - 1):
				dest = get_elem_of_type(ix - offset, iy, dest_type)
				connect(src, dest)
			if ix < (nx - offset):
				dest = get_elem_of_type(ix + offset, iy, dest_type)
				connect(src, dest)
			if iy > (offset - 1):
				dest = get_elem_of_type(ix, iy - offset, dest_type)
				connect(src, dest)
			if iy < (ny - offset):
				dest = get_elem_of_type(ix, iy + offset, dest_type)
				connect(src, dest)


def dump_grid():
	f_out = open('d.json', 'w')
	f_out.write('[\n')
	first = True
	for ix in xrange(nx):
		for iy in xrange(ny):
			for n in grid[ix][iy]:
				if not first:
					f_out.write(',\n')
				f_out.write('\t' + n.toJSON())
				first = False

	f_out.write('\n]')


create_elems_of_type('A')
create_elems_of_type('B', 0, 1)
create_elems_of_type('C', 0, 2)
connect_neighbours('A', 'A', 1)
connect_neighbours('A', 'A', 3)
#connect_neighbours('B', 'B')
#connect_neighbours('C', 'C')
connect_neighbours('A', 'B')
connect_neighbours('B', 'C')
connect_neighbours('C', 'A')
dump_grid()