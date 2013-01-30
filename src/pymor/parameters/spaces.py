from __future__ import absolute_import, division, print_function, unicode_literals

from collections import OrderedDict
from itertools import izip, product
import numpy as np

import pymor.core as core
from .interfaces import ParameterSpaceInterface
from .base import parse_parameter, parse_parameter_type, Parameter


class CubicParameterSpace(ParameterSpaceInterface):

    def __init__(self, parameter_type, minimum=None, maximum=None, ranges=None):
        assert ranges is None or (minimum is None and maximum is None), 'Must specify minimum, maximum or ranges'
        assert ranges is not None or (minimum is not None and maximum is not None), 'Must specify minimum, maximum or ranges'
        assert minimum is None or minimum < maximum
        parameter_type = parse_parameter_type(parameter_type)
        self.parameter_type = parameter_type
        if ranges is None:
            ranges = OrderedDict((k, (minimum, maximum)) for k in parameter_type)
        self.ranges = ranges

    def parse_parameter(self, mu):
        return parse_parameter(mu, self.parameter_type)

    def contains(self, mu):
        mu = self.parse_parameter(mu)
        return all(np.all(self.ranges[k][0] <= mu[k]) and np.all(mu[k] <= self.ranges[k][1]) for k in self.parameter_type)

    def sample_uniformly(self, counts):
        if isinstance(counts, dict):
            pass
        elif isinstance(counts, (tuple, list, np.ndarray)):
            counts = {k:c for k,c in izip(self.parameter_type, counts)}
        else:
            counts = {k:counts for k in self.parameter_type}
        linspaces = tuple(np.linspace(self.ranges[k][0], self.ranges[k][1], num=counts[k]) for k in self.parameter_type)
        iters = tuple(product(ls, repeat=max(1,np.zeros(sps).size))
                                for ls,sps in izip(linspaces, self.parameter_type.values()) )
        for i in product(*iters):
            yield Parameter((k, np.array(v).reshape(shp))
                                          for k, v, shp in izip(self.parameter_type, i, self.parameter_type.values()))

    def sample_randomly(self, count=None):
        c = 0
        while count is None or c < count:
            yield Parameter((k, np.random.uniform(r[0], r[1], shp)) for k, r, shp in
                                          izip(self.parameter_type, self.ranges.values(), self.parameter_type.values()))
            c += 1
