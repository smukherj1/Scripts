import os
import subprocess as subp

'''
Internal implementation functions and variables
'''
_core_count_cached = None
def _parseWMICOutput(output):
	global _core_count_cached
	for line in output:
		line = line.strip()
		if not line:
			continue
		line = line.split('=')
		if line[0].strip().lower() == 'numberofcores':
			_core_count_cached = int(line[1].strip())
			break
	if _core_count_cached == None:
		_core_count_cached = -1
	return

def _getWindowsCPUPhysicalCoreCount():
	p = subp.Popen(['wmic', 'CPU', 'Get', '/Format:List'], stdout=subp.PIPE, stderr=subp.PIPE)
	ret = p.wait()
	if ret != 0:
		global _core_count_cached
		_core_count_cached = -1
	else:
		_parseWMICOutput(p.stdout.readlines())

	return

'''
The public API to get the physical core count
'''
def getCPUPhysicalCoreCount():
	if _core_count_cached != None:
		return _core_count_cached
	if os.name == 'nt':
		_getWindowsCPUPhysicalCoreCount()
	else:
		raise OSError('Unsupported OS: ' + os.name)

	return _core_count_cached


if __name__ == '__main__':
	print getCPUPhysicalCoreCount()