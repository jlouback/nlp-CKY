__author__="Juliana Louback <jl4354@.columbia.edu>"

import sys
import json
import fileinput
import logging
from collections import defaultdict


"""
Function to get unitary rule counts, binary rule counts and
nonterminal counts, organized in dictionaries.

Used in cky.py

"""

def get_counts(filename):
    nonterminal_count = dict()
    unary_count = dict()
    binary_count = dict()
    # Obtain the count(X->YZ), count(X->w), count(X)
    # rather, the binary and unary rule counts, and the
    # non terminal counts
    train_count = file(filename,"r")
    line = train_count.readline()
    while line:
        parts = line.strip().split(" ")
        line_type = parts[1]
        count = parts[0]
        # Get nonterminal counts = count(X)
        if "TERMINAL" in line_type:
            nonterminal = parts[2]
            nonterminal_count[nonterminal] = count
        # Get unary rule count = count(X->w)
        if "UNARY" in line_type:
            nonterminal = parts[2]
            word = parts[3]
            if nonterminal in unary_count:
                unary_count[nonterminal].update({word:count})
            else:
                unary_count[nonterminal] = {word:count}
        # Get binary rule count = count(x->YZ)
        if "BINARY" in line_type:
            x = parts[2]
            y = parts[3]
            z = parts[4]
            key = y + " " + z
            if x in binary_count:
                binary_count[x].update({key:count})
            else:
                binary_count[x] = {key:count}
        line = train_count.readline()
    return nonterminal_count, unary_count, binary_count

# Returns true if word is not seen in training data
# (ergo not in unary rules)
def is_rare(word, unary_count):
    for item in unary_count:
        for words in unary_count[item]:
            if word == words:
                return False
    return True

# Replaces words unseen in training data with _RARE_
def replace_rare(line, unary_count):
    parts = line.split(" ")
    replaced = line
    for word in parts:
        if is_rare(word, unary_count):
            replaced = replaced.replace(word, "_RARE_")
    return replaced

