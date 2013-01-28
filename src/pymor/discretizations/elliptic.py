from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
from scipy.sparse.linalg import bicg
from scipy.sparse import issparse

import pymor.core as core
from pymor.domaindescriptions import BoundaryType
from pymor.parameters import Parametric


class EllipticDiscretization(Parametric):

    def __init__(self, operator, rhs, solver=None, visualizer=None):
        self.operator = operator
        self.operators = {operator.name: operator}
        self.rhs = rhs
        self.set_parameter_type(inherits={'operator':operator, 'rhs':rhs})

        def default_solver(A, RHS):
            if issparse(A):
                U, info = bicg(A, RHS)
            else:
                U = np.linalg.solve(A, RHS)
            return U
        self.solver = solver or default_solver

        if visualizer is not None:
            self.visualize = visualizer


    def solve(self, mu={}):
        A = self.operator.matrix(self.map_parameter(mu, 'operator'))
        RHS = self.rhs.matrix(self.map_parameter(mu, 'rhs'))
        return self.solver(A, RHS)
