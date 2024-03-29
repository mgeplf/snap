"""
Morphology access.
"""

"""
Copyright (c) 2019, EPFL/Blue Brain Project

This file is part of BlueBrain SNAP library <https://github.com/BlueBrain/snap>

This library is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License version 3.0 as published
by the Free Software Foundation.

This library is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License
along with this library; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import os

import numpy as np
import neurom as nm

from bluesnap.settings import MORPH_CACHE_SIZE


class MorphHelper(object):
    """ Collection of morphology-related methods. """

    def __init__(self, morph_dir, nodes):
        self._morph_dir = morph_dir
        self._nodes = nodes
        self._load = nm.load_neuron
        if MORPH_CACHE_SIZE is not None:
            try:
                from functools import lru_cache
            except ImportError:  # pragma: nocover
                from functools32 import lru_cache
            self._load = lru_cache(maxsize=MORPH_CACHE_SIZE)(self._load)

    def get_filepath(self, gid):
        """ Return path to SWC morphology file corresponding to `gid`. """
        name = self._nodes.get(gid, 'morphology')
        return os.path.join(self._morph_dir, "%s.swc" % name)

    def get(self, gid, transform=False):
        """
        Return NeuroM morphology object corresponding to `gid`.

        If `transform` is True, rotate and translate morphology points
        according to `gid` position in the circuit.
        """
        filepath = self.get_filepath(gid)
        result = self._load(filepath)
        if transform:
            A_t = self._nodes.orientations(gid).transpose()
            B = self._nodes.positions(gid).values
            result = result.transform(lambda p: np.dot(p, A_t) + B)
        return result
