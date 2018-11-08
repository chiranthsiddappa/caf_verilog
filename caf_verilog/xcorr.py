
def simple_xcorr(f, g, nlags):
    """

    :param f:
    :param g:
    :param nlags:
    :return:
    """
    sums = []
    space = range(-nlags, nlags + 1)
    for n in space:
        sum = 0
        for m in range(0, len(g)):
            cc_index = m + n
            if cc_index >= 0 and cc_index < len(g):
                sum += f[m] * g[cc_index]
        sums.append(sum)
    return sums, space


def size_visualization(f, g, nlags):
    space = range(-nlags, nlags + 1)
    for n in space:
        n_indexes = []
        for m in range(0, len(g)):
            cc_index = m + n
            if cc_index >= 0 and cc_index < len(g):
                n_indexes.append((m, cc_index))
        spacing = " " * int(n >= 0)
        print("n: " + spacing + str(n) + " " + str(n_indexes))