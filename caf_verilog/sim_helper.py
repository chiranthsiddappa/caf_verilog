def sim_shift(ref, ref_center, ref_length, shift=0, rec=None, padding=False):
    """

    :param ref: Reference signal.
    :param ref_center: Where to center the simulated signal set.
    :param ref_length: The length of the signal equidistant around center.
    :param shift: How much shift should be added to the simulated received signal.
    :param rec: A received signal can be provided for the correlation simulation.
    :param padding: Use padding to add zeros on the reference signal; ex. for generating a plot.
    :return: ref, rec
    :rtype: tuple
    """
    sim_center = ref_center + shift
    fill_length = int(ref_length / 2)
    index_error = not ((ref_center - ref_length) > 0)
    index_error |= not ((ref_center + ref_length) < len(ref))
    if index_error:
        raise IndexError("Center and length result in an out of bounds error in ref")
    if rec:
        index_error |= not ((ref_center + ref_length) < len(rec))
        if index_error:
            raise IndexError("Center and length result in an out of bounds error in rec")
    ref_ret = ref[ref_center - fill_length: ref_center + fill_length]
    if padding:
        fill_zeros = [0 for zz in range(0, fill_length)]
        ref_ret = fill_zeros + list(ref_ret)
        ref_ret += fill_zeros
    if rec:
        rec_ret = rec[sim_center - ref_length:sim_center + ref_length]
    else:
        rec_ret = ref[sim_center - ref_length: sim_center + ref_length]
    return ref_ret, rec_ret
