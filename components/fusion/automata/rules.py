from ..conf.postures import to_vec

def match_any(*postures):
    """
    Returns a rule to match one or more postures with the input mask that is True when
    at least one of the postures matches with the input mask, else False
    :param postures: One or more postures as strings
    :return: Rule to match the input postures with the input mask
    """
    posture_vecs = [to_vec[posture] for posture in postures]

    def f(in_sym):
        for v in posture_vecs:
            if (in_sym & v) == v:
                return True
        return False

    return f


def match_all(*postures):
    """
    Returns a rule to match one or more postures with the input mask that is True when
    all of the postures match with the input mask, else False
    :param postures: One or more postures as strings
    :return: Rule to match the input postures with the input mask
    """
    posture_vecs = [to_vec[posture] for posture in postures]

    def f(in_sym):
        for v in posture_vecs:
            if (in_sym & v) != v:
                return False
        return True

    return f


def mismatch_any(*postures):
    """
    Returns a rule to match one or more postures with the input mask that is True when
    at least one of the postures does not match with the input mask, else False
    :param postures: One or more postures as strings
    :return: Rule to match the input postures with the input mask
    """

    posture_vecs = [to_vec[posture] for posture in postures]

    def f(in_sym):
        for v in posture_vecs:
            if (in_sym & v) != v:
                return True
        return False

    return f


def mismatch_all(*postures):
    """
    Returns a rule to match one or more postures with the input mask that is True when
    none of the postures matches with the input mask, else False
    :param postures: One or more postures as strings
    :return: Rule to match the input postures with the input mask
    """
    posture_vecs = [to_vec[posture] for posture in postures]

    def f(in_sym):
        for v in posture_vecs:
            if (in_sym & v) == v:
                return False
        return True

    return f


# Meta rule for ANDing
def and_rules(*rules):
    """
    Returns a rule that computes the logical AND of the input rules with the input mask
    :param rules: One or more boolean rules
    :return: Rule that is logical AND of the input boolean rules
    """
    def f(in_sym):
        for rule in rules:
            if not rule(in_sym):
                return False
        return True

    return f


# Meta rule for ORing
def or_rules(*rules):
    """
    Returns a rule that computes the logical OR of the input rules with the input mask
    :param rules: One or more boolean rules
    :return: Rule that is logical OR of the input boolean rules
    """
    def f(in_sym):
        for rule in rules:
            if rule(in_sym):
                return True
        return False

    return f
