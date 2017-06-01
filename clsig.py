import os
import sys
import json

import clang.cindex

class ClassDB:
	def __init__(self):
		self._data = {}
		self._supported_kinds = set(
			[clang.cindex.CursorKind.CLASS_DECL,
			clang.cindex.CursorKind.STRUCT_DECL]
		)

	def __call__(self, cursor):
		if cursor.kind not in self._supported_kinds:
			return
		cursor_type = cursor.type
		if cursor_type.spelling in self._data:
			return
		fields = []
		for ifield in cursor_type.get_fields():
			fields.append([ifield.displayname, ifield.type.spelling])
		if fields:
			self._data[cursor_type.spelling] = fields
		return

	@property
	def data(self):
		return self._data


def recurse_visit_tu(tu, callback):
	cursor_stack = [tu.cursor]
	while cursor_stack:
		next_cursor = cursor_stack.pop()
		callback(next_cursor)
		for ichild_cursor in next_cursor.get_children():
			cursor_stack.append(ichild_cursor)
	return

if __name__ == '__main__':
	CLANG_ROOT = os.environ.get('CLANG_ROOT')
	OS_MAP = {
		'posix' : 'linux64',
		'nt' : 'windows64'
	}
	clang.cindex.Config.set_library_path(os.path.join(CLANG_ROOT, OS_MAP.get(os.name), 'lib'))
	in_filename = sys.argv[1]
	out_filename = sys.argv[2]
	args = []
	if len(sys.argv) > 3:
		args = sys.argv[3:]
	tu = clang.cindex.Index.create().parse(in_filename, args=args)
	num_diags = 0
	for idiag in tu.diagnostics:
		print idiag
		num_diags += 1
	if num_diags > 0:
		exit(1)
	class_db = ClassDB()
	recurse_visit_tu(tu, class_db)

	json.dump(class_db.data, open(out_filename, 'w'))