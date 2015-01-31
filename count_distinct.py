import sys

if __name__ == '__main__':
	# The first and only argument should be a filename where
	# each of the words we need to count distinctly appear on
	# different lines
	if len(sys.argv) != 2:
			print 'Error: Expected exactly one command line argument for the filename'
			exit(1)
	try:
		f_in = open(sys.argv[1])
	except IOError:
		print 'Error: Could not open %s as a file.'%sys.argv[1]
		exit(1)

	wordmap = {}
	for line in f_in:
		line = line.strip()
		if line in wordmap:
			wordmap[line] += 1
		else:
			wordmap[line] = 1

	f_out = open('out.txt', 'w')
	for word in wordmap:
		f_out.write('%s\t%s\n'%(word, wordmap[word]))