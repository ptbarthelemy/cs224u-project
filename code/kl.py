def kldiv(s, t):
    import math
    ssum = 0. + sum(s)
    slen = len(s)
        
    tsum = 0. + sum(t)
    tlen = len(t)

    """ Check if distribution probabilities sum to 1"""
    sc = sum([v/ssum for v in s])
    st = sum([v/tsum for v in t])
    
    if sc < 9e-6:
        print "Sum P: %e, Sum Q: %e" % (sc, st)
        print "*** ERROR: sc does not sum up to 1. Bailing out .."
        sys.exit(2)
    if st < 9e-6:
        print "Sum P: %e, Sum Q: %e" % (sc, st)
        print "*** ERROR: st does not sum up to 1. Bailing out .."
        sys.exit(2)

    div = 0.
    for i, v in enumerate(s):
        pts = v / ssum
        ptt = t[i] / tsum
        if pts == 0.0 or ptt == 0.0:
            ckl = 0.0
        else:
            ckl = (pts - ptt) * math.log(pts / ptt)
        div +=  ckl

    return div
