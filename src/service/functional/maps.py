from typing import Mapping


def querymap(q: Mapping):
    return {k: q[k] for k in q if q[k] is not ...}
