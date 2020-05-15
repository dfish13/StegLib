import subprocess
from util import color_distance

def blossom_perfect_matching(color_table):
    """
    Args:
        color_table is a list of (r, g, b) tuples of even length.

    Description:
        returns a reordering based on the perfect matching.
    """
    output = run_blossom_subprocess('../blossom5', make_blossom_graph_string(color_table))
    output = output.split()
    i = 0
    while output[i] != 'Duncanwashere':
        i += 1
    i += 3
    output = output[i:]
    new_color_table = []
    for i in output:
        new_color_table.append(color_table[int(i)])
    return [int(x) for x in output]



def run_blossom_subprocess(path_to_blossom, in_string):
    """
    Args:
        path_to_blossom is the path to the C++ blossom5 executable.
        in is the input string being redirected to stdin.

    Description:
        executes blossom5 as a subprocess and returns standard
        output as a string.
    """
    proc = subprocess.Popen([path_to_blossom, '-P', '-e', 'stdin'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    outs, errs = proc.communicate(input=in_string.encode('utf-8'))
    return outs.decode('utf-8')


def make_blossom_graph_string(color_table):
    """
    Args:
        color_table is a list of (r, g, b) tuples.

    Description:
        Makes a weighted graph where there is an edge between every
        node and the weight of the edge is the distance between the
        colors in rgb space. Returns this graph as a string in
        blossom4 format.
    """
    l = len(color_table)
    s = '{} {}\n'.format(l, l*(l-1)//2)
    for i in range(l):
        for j in range(i+1, l):
            d = color_distance(color_table[i], color_table[j])
            s += '{} {} {}\n'.format(i, j, d)
    return s

def make_blossom_graph_file(color_table, outfilename):
    with open(outfilename, 'w') as outfile:
        outfile.write(make_blossom_graph_string(color_table))
