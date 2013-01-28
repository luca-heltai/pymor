from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np

import pymor.core as core
from pymor.parameters import Parametric

class DiscreteOperatorInterface(core.BasicInterface, Parametric):

    __name = None
    @property
    def name(self):
        if self.__name is None:
            import uuid
            self.__name = str(uuid.uuid4())
        return self.__name

    @name.setter
    def name(self, n):
        if self.__name is not None:
            raise AttributeError('Name has already been set and cannot be changed')
        else:
            self.__name = n

    source_dim = 0
    range_dim = 0

    @core.interfaces.abstractmethod
    def apply(self, U, mu={}, axis=-1):
        pass


class LinearDiscreteOperatorInterface(DiscreteOperatorInterface):

    @core.interfaces.abstractmethod
    def assemble(self, mu={}):
        pass

    def matrix(self, mu={}):
        mu = self.parse_parameter(mu)
        if self._last_mu is not None and self._last_mu.allclose(mu):
            return self._last_mat
        else:
            self._last_mu = mu.copy() # TODO: add some kind of log message here
            self._last_mat = self.assemble(mu)
            return self._last_mat

    def apply(self, U, mu={}):
        return matrix(mu).dot(U)  # TODO: Check what dot really does for a sparse matrix

    _last_mu = None
    _last_mat = None