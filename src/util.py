

def color_distance(c1, c2):
    return sum((x-y)**2 for x, y in zip(c1, c2))

def greedy_tsp_3d(gct):
	x_gct = gct.copy()
	color = x_gct[0]
	x_gct.remove(color)
	perm = []
	perm.append(gct.index(color))
	while x_gct:
		min_distance = None
		for xcolor in x_gct:
			d = color_distance(xcolor, color)
			if min_distance is None or d < min_distance:
				min_distance = d
				min_color = xcolor
		color = min_color
		perm.append(gct.index(color))
		x_gct.remove(color)
	return perm

def apply_permutation(perm, color_table, index_stream):
	new_color_table = []
	inv_perm = list.copy(perm)
	for i, x in enumerate(perm):
		new_color_table.append(color_table[x])
		inv_perm[x] = i

	new_index_stream = [inv_perm[x] for x in index_stream]
	return new_color_table, new_index_stream
