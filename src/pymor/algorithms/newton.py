# This file is part of the pyMOR project (http://www.pymor.org).
# Copyright Holders: Rene Milk, Stephan Rave, Felix Schindler
# License: BSD 2-Clause License (http://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function

import numpy as np

from pymor import defaults
from pymor.core import getLogger
from pymor.core.exceptions import InversionError, NewtonError


def newton(operator, rhs, initial_guess=None, mu=None, error_norm=None,
           miniter=None, maxiter=None, reduction=None, abs_limit=None,
           stagnation_window=None, stagnation_threshold=None,
           return_stages=False, return_residuals=False):
    miniter = defaults.newton_miniter if miniter is None else miniter
    maxiter = defaults.newton_maxiter if maxiter is None else maxiter
    reduction = defaults.newton_reduction if reduction is None else reduction
    abs_limit = defaults.newton_abs_limit if abs_limit is None else abs_limit
    logger = getLogger('pymor.algorithms.newton')

    data = {}

    if initial_guess is None:
        initial_guess = operator.type_source.zeros(operator.dim_source)

    if return_stages:
        data['stages'] = operator.type_source.empty(operator.dim_source)

    if return_residuals:
        data['residuals'] = operator.type_range.empty(operator.dim_range)

    U = initial_guess.copy()
    residual = rhs - operator.apply(U, mu=mu)

    err = residual.l2_norm()[0] if error_norm is None else error_norm(residual)[0]
    logger.info('      Initial Residual: {:5e}'.format(err))

    iteration = 0
    error_sequence = [err]
    while (iteration < miniter
           or (iteration < maxiter
               and err > abs_limit and err/error_sequence[0] > reduction
               and (len(error_sequence) < stagnation_window + 1
                    or err/max(error_sequence[-stagnation_window - 1:]) < stagnation_threshold))):
        if iteration > 0 and return_stages:
            data['stages'].append(U)
        if return_residuals:
            data['residuals'].append(residual)
        iteration += 1
        jacobian = operator.jacobian(U, mu=mu)
        try:
            correction = jacobian.apply_inverse(residual)
        except InversionError:
            raise NewtonError('Could not invert jacobian')
        U += correction
        residual = rhs - operator.apply(U, mu=mu)

        err = residual.l2_norm()[0] if error_norm is None else error_norm(residual)[0]
        logger.info('Iteration {:2}: Residual: {:5e},  Reduction: {:5e}, Total Reduction: {:5e}'
                    .format(iteration, err, err / error_sequence[-1], err / error_sequence[0]))
        error_sequence.append(err)

    if (err <= abs_limit):
        logger.info('Absolute limit of {} reached. Stopping.'.format(abs_limit))
    elif (err/error_sequence[0] <= reduction):
        logger.info('Prescribed total reduction of {} reached. Stopping.'.format(reduction))
    elif (len(error_sequence) >= stagnation_window + 1
          and err/max(error_sequence[-stagnation_window - 1:]) >= stagnation_threshold):
        logger.info('Error is stagnating (threshold: {:5e}, window: {}). Stopping.'.format(stagnation_threshold,
                                                                                           stagnation_window))
    else:
        raise NewtonError('Failed to converge')

    data['error_sequence'] = np.array(error_sequence)

    return U, data
