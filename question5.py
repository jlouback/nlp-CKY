from question5_utils import is_rare
from question5_utils import get_counts
import sys
import operator
import logging
import json
import timeit

"""
Usage:
python question5.py cfg.counts parse_dev.dat > [output_file]

Question 5:  Using the counts file, it calculates the maximum likelihood estimates for the PCFG rules,
then generates the tree with max probability per line of parse_dev.dat represented in the JSON tree format.

Uses functions in question5_utils.py, namely to organize unary, binary and nonterminal counts into dictionaries.
First run

python count_cfg_freq.py parse_train.dat > cfg.counts
python question4.py cfg.counts parse_train.dat
python count_cfg_freq.py parse_train.dat > cfg.counts

to replace words with count < 5 with _RARE_

"""

def cky(words, binary_count, unary_count, nonterminal_count):
    # Initialize lookup chart with unary rules on diagonal and
    # their respective probabilities in the probability matrix
    n = len(words)
    chart = [[{} for i in range(n+1)] for j in range(n)]
    backpointers = [[{} for i in range(n+1)] for j in range(n)]

    for i in range(n):
        word = words[i]
        # Check if word is rare, act accordingly
        if is_rare(word, unary_count):
            word = "_RARE_"
        for X in unary_count:
            if word in unary_count[X]:
                q = float(unary_count[X][word])/float(nonterminal_count[X])
                chart[i][i+1].update({X:q})
                backpointers[i][i+1][X] = [words[i]]

    # Building bottom-up from the unary rules on the diagonal, connect non-terminals
    # into binary rules.
    for l in range(2, n+1):
        for i in range(n-l+1):
            j = l + i
            for s in range(i+1,j):
                for X in binary_count:
                    for key in binary_count[X]:
                        Y = key.split(" ")[0]
                        Z = key.split(" ")[1]
                        if Y in chart[i][s] and Z in chart[s][j]:
                            q = float(binary_count[X][key])/float(nonterminal_count[X])
                            probability = float(chart[i][s][Y])*float(chart[s][j][Z])* q
                            if X in chart[i][j]:
                                if probability > chart[i][j][X]:
                                    chart[i][j][X] = probability
                                    backpointers[i][j][X] = [s,Y,Z]
                            else:
                                chart[i][j][X] = probability
                                backpointers[i][j][X] = [s,Y,Z]
    return chart, backpointers

# returns max probability parse tree starting with 'S'; if no tree starting with 'S' exists, the arg max tree
# starting with any nonterminal.
def trace(root, i, j):
    if len(backpointers[i][j][root]) == 1:
        return [root, backpointers[i][j][root]]
    else:
        s = backpointers[i][j][root][0]
        Y = backpointers[i][j][root][1]
        Z = backpointers[i][j][root][2]
        return [root, trace(Y,i,s), trace(Z,s,j)]

# To get script runtime (optional)
start = timeit.default_timer()

# Obtain the count(X->YZ), count(X->w), count(X), A.K.A,  the binary, unary and non-terminal counts
# (see questions5_utils.py)
nonterminal_count, unary_count, binary_count = get_counts(sys.argv[1])

# Read dev file line by line
dev_data = file(sys.argv[2],"r")
line = dev_data.readline().strip()
while line:
    words = line.split(" ")
    chart, backpointers = cky(words, binary_count, unary_count, nonterminal_count)
    n = len(words)
    # Get parse tree of max probability starting with 'S'
    if 'S' in backpointers[0][n]:
        tree = trace('S',0,n)
    # If there are no valid parse trees starting with 'S', get arg max starting with any nonterminal
    else:
        X = max(chart[0][n].iteritems(), key=operator.itemgetter(1))[0]
        tree = trace(X,0,n)
    # tree is in list form, convert to JSON for compatibility, write to output file
    data = json.dumps(tree)
    sys.stdout.write(data)
    sys.stdout.write("\n")
    line = dev_data.readline().strip()
    # In case you want to see the parse trees as they are produced for each sentence
    #logging.warning(data)

stop = timeit.default_timer()
logging.warning('Runtime:')
logging.warning(stop - start)
