__author__="Juliana Louback <jl4354@.columbia.edu>"

import sys
import json
import fileinput
import logging
from collections import defaultdict

"""
Usage:
python relabel_rare.py cfg.counts parse_train.dat

Replace infrequent words (Count(x) < 5) in the 
original training data file with a common symbol RARE .
It modifies the training data file directly.

Note: First run python count_cfg_freq.py parse_train.dat > cfg.counts
with the original training data file

"""
# Function for going through tree, returning a dictionary
# containing the leaves of the tree: key=word, value=tag
# (Terminals in a PCFG)
def walk(tree, leaves):
	if len(tree) == 3:
		walk(tree[1], leaves)
		walk(tree[2], leaves)
	else:
		leaves[tree[1]] = tree[0]

#Get counts file, read training data, store infrequent words 
counts = file(sys.argv[1],"r")
rare_words = defaultdict()
line = counts.readline()
while line:
	if "UNARYRULE" in line:
		parts = line.strip().split(" ")
		count = int(parts[0])
		word = parts[3]
		tag = parts[2]
		# A rare word can have more than one tag association
		if count < 5:
			if word in rare_words:
				rare_words[word].append(tag)
			else:
				rare_words[word] = [tag]
	line = counts.readline()

#Go through training data file
for line in fileinput.input(sys.argv[2], inplace=1):
	tree = json.loads(line)
	# Go to leaves, if word in rare_words, relabel as _RARE_
	leaves = dict()
	walk(tree, leaves)
	for word, tag in leaves.items():
		if word in rare_words:
			for rare_tag in rare_words[word]:
				# Need to check if both tag and word are in rare words
				if tag == rare_tag:
					# Need to check for the combo, as the word can be present in 
					# the sentence but not be a rare word-tag combo.
					old_tag = "\"" + tag + "\", \"" + word + "\""
					new_tag = "\"" + tag + "\", \"_RARE_\""
					line = line.replace(old_tag, new_tag)
	sys.stdout.write(line)



