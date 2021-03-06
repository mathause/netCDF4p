#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Mathias Hauser
# Date: 14.12.2014

from __future__ import print_function

import netCDF4

from netCDF4 import Group, CompoundType, stringtoarr, \
default_encoding, default_fillvals, MFTime, num2date, date2num, \
date2index, __has_rename_grp__, stringtochar, chartostring, \
getlibversion, __hdf5libversion__, __netcdf4libversion__, __version__, \
is_native_little

import netCDF4.utils

from collections import OrderedDict
from functools import wraps
import numpy as np
from glob import glob


# coordinate subseting/ indexing


# Given you have a variable with the dimensions time x lat x lon you can
# select a region as follows:

# ncf = nc.Dataset(file)
# T = ncf.variables['temp'][:, {lat_from, lat_to}, {lon_from, lon_to}]

# it will look for the coordinate that is closest to lat_from and this will
# give the first index.
# If 
# lat = [0, 10, 20, 30, 40, 50, 60 70, 80, 90], lat_from = 15 and lat_to = 30, 
# {lat_from, lat_to} will be 'replaced' by slice(2, 4 + 1)


# SUBCLASS Dataset and Variable
# ---------------------------------------------------------------------------


def _select(self, item):

    if len(item) > 3:
        raise IndexError("selector for dimension %i (%s) has \
            too many elements" % ("XXXX", "XXX"))


    if self.variable is None:
        raise RuntimeError("dimension '{name}' has no data".format(
            name=self.name))

    data = self.variable[:]
    
    start = wherenearest(data, item[0])
    stop = start if len(item) < 2 else wherenearest(data, item[1])
    step = 1 if len(item) < 3 else item[2]

    # reverse start stop if dimen is sorted the other way round
    if start > stop:
        start, stop = stop, start
    # python slice notation: stop is the first that is NOT selected
    sel = slice(start, stop + 1, step)

    vals = data[sel]
    if self.verbose:
        print_selection(self.name, item, vals[0], stop_val=vals[-1])
    return sel

# ---------------------------------------------------------------------------


def print_selection(name, item, start_val, stop_val):
    """print item and resulting selection"""
    string = "Select '{0}': ".format(name)

    if len(item) == 1:
        msg = "{0}{1} selects: {2:5.3f}".format(string, item[0], start_val)
    elif len(item) == 2:
        msg = ("{0}{1}...{2} selects: {3:5.3f}...{4:5.3f}".
               format(string, item[0], item[1], start_val, stop_val))

    print(msg)

# ============================================================================


class Select(object):

    """docstring for select"""

    def __init__(self, name, dimension, variable, verbose=True):
        super(Select, self).__init__()

        self.name = name
        self.dimension = dimension
        self.variable = variable

        self.verbose = verbose

        # se
        self.selections = OrderedDict()

    def __getitem__(self, item):

        # as 'set' is sorted it is not possible to pass a 'step'
        if isinstance(item, set):
            if len(item) == 3:
                raise IndexError("Can not pass a step argument with a set")
            elif len(item) not in [1, 2]:
                raise IndexError(
                    "When providing a set {}, it must have 1 or 2 elements")

        # check size if tuple is passed (named argument)
        if len(item) not in [1, 2, 3]:
            raise IndexError("When providing a named selection, "
                             "it must have 1, 2 or 3 elements")

        # convert to tuple (must be hashable)
        item = tuple(item)

        # check if this particular case was already selected
        sel = self.selections.get(item, None)

        if sel is None:
            # get the new selection

            sel = _select(self, item)

            # assign the new selection to the dict
            self.selections[item] = sel

        return sel

    # selections can not be assigned
    def __setitem__(self, item, value):
        raise RuntimeError("Coordinate Subscripts can not be set manually")

# ============================================================================


def wherenearest(grid, pos):
    """return index nearest to pos"""

    if grid.ndim != 1:
        raise RuntimeError("Can not select if coordinate is not 1-Dimensional")

    val = np.abs(grid - pos)
    IDX = np.where(val == np.min(val))
    return IDX[0][0]

# ============================================================================
# subclass the netCDF4.Dataset class in order to (1) use the new Variable
# class and (2) the Select class


class Dataset(netCDF4.Dataset):

    """subclass of netCDF4.Dataset that uses the """

    #select = dict()

    def __init__(self, *arg, **kwargs):

        # get ncp specific arguments
        verbose = kwargs.pop('verbose', True)
        select = kwargs.pop('select', None)
        
        try:
            super(Dataset, self).__init__(*arg, **kwargs)
        except RuntimeError:
            raise RuntimeError("No such file or directory '%s'" % arg[0])

        self.__dict__.update(self.__getattr__('__dict__'))

        if select is None:
            self.__dict__['select'] = OrderedDict()
        else:
            self.__dict__['select'] = select


        # unfortunately we have to reassign "variables" in order to
        # use the new version (of 'Variable')
        for var, ncv in self.variables.iteritems():
            self.variables[var] = Variable(ncv.group(),
                                           ncv._name,
                                           ncv.datatype,
                                           ncv.dimensions,
                                           id=ncv._varid,
                                           select_parent=self.select
                                           )

        # add the new Select class to the Dataset
        for dim, ncd in self.dimensions.iteritems():
            self.select[dim] = Select(dim,
                                      ncd,
                                      self.variables.get(dim, None),
                                      verbose=verbose
                                      )


# ============================================================================
# subclass the netCDF4.MFDataset class in order to (1) use the new Variable
# class and (2) the Select class

class MFDataset(netCDF4.MFDataset):

    """subclass of netCDF4.Dataset that uses the """

#    select = dict()

    def __init__(self, *arg, **kwargs):

        try:
            super(MFDataset, self).__init__(*arg, **kwargs)
        except RuntimeError:
            raise RuntimeError("No such file or directory '%s'" % arg[0])

        verbose = kwargs.get('verbose', True)

        self.__dict__['select'] = OrderedDict()

        # unfortunately we have to reassign "variables" in order to
        # use the new version
        for var, ncv in self.variables.iteritems():


            if isinstance(ncv, netCDF4.Variable):
                self._vars[var] = Variable(ncv.group(),
                                           ncv._name,
                                           ncv.datatype,
                                           ncv.dimensions,
                                           id=ncv._varid,
                                           select_parent=self.select
                                           )
            else:
                self._vars[var] = _Variable(self,
                                            ncv._name,
                                            ncv._mastervar,
                                            ncv._recdimname,
                                            select_parent=self.select
                                            )

        # add the new Select class to the Dataset
        for dim, ncd in self.dimensions.iteritems():
            self.select[dim] = Select(dim,
                                      ncd,
                                      self.variables.get(dim, None),
                                      verbose=verbose
                                      )



# ============================================================================


class MSFDataset(object):

    """docstring for MSFDataset"""

    def __init__(self, files, check=False, aggdim=None, exclude=[],
                 verbose=True):
        super(MSFDataset, self).__init__()

        # Open the master file in the base class, so that the CDFMF instance
        # can be used like a CDF instance.
        if isinstance(files, str):
            if files.startswith('http'):
                msg = 'cannot use file globbing for remote (OPeNDAP) datasets'
                raise ValueError(msg)
            else:
                files_in = files
                files = sorted(glob(files))

            if len(files) == 0:
                msg = "No such file: '{0}'".format(files_in)
                raise RuntimeError(msg)


        master = files[0]

        cdfm = Dataset(master)
        # copy attributes from master.
        for name, value in cdfm.__dict__.items():
            self.__dict__[name] = value

        self._files = files

        ncfs = []

        for _file in files[2:]:
            ncfs.append(Dataset(_file, select=self.select,
                                verbose=verbose))

        self._ncfs = ncfs

    def __getitem__(self, key):
        return self._ncfs[key]

    def __iter__(self):
        return self._ncfs.__iter__()

    def __len__(self):
        return self._ncfs.__len__()


# ============================================================================


# subclass netCDF4.Variable to alter __getitem__

def __expand_elem__(self, elem):
    """parse the slice input"""

    ndim = self.ndim
    # scalar variables can have ndim = 0
    if ndim == 0:
        ndim = 1

    # PARSE ELEM
    # we need to be sure of the position of all elem

    # (1) only 1 elem is given
    if not isinstance(elem, tuple):
        elem = (elem, )

    # search for named elements (dicts)
    had_dict = False

    _elem = ()
    _dict = dict()

    # loop through given elements to
    # (1) collect all named arguments (dict)
    # (2) make sure a named argument is not followed by a non-named arg
    for i, el in enumerate(elem):
        if isinstance(el, dict):
            had_dict = True
            _dict.update(el)
        elif had_dict:
            raise SyntaxError("non-keyword arg after keyword arg ('dict')")
        else:
            _elem = _elem + (el, )
    elem = _elem

    # (2) make sure there are not too many dimensions in slice.
    if len(elem) > ndim:
        raise ValueError("slicing expression exceeds the number of dimensions \
            of the variable")

    # (2) if less elements are given than there are dimensions:
    #     fill them with Ellipsis

    missing_dim = ndim - len(elem)

    # Note: netCDF4 replaces Ellipsis with slice(None)
    if missing_dim > 0:
        # the first occurence of Ellipsis gets expanded
        try:
            # find index of first occurence of Ellipsis
            i = next(el[0] for el in enumerate(elem) if np.all(el[1] == Ellipsis))
            # expand
            elem = elem[:i + 1] + (slice(None), ) * missing_dim + elem[i + 1:]
        except StopIteration: # no Ellipsis found
            # add 'Ellipsis' at end
            elem = elem + (slice(None), ) * missing_dim

    return elem, _dict

# ----------------------------------------------------------------------------


def __parse_el__(self, elem, _dict):
    """find slices that have to be selected"""

    sel_elem = list()

    # select positional arguments if necessary
    for i, el in enumerate(elem):

        # coordinate subsetting happens for sets
        if isinstance(el, set):

            # name of the dimension
            dim = self.dimensions[i]

            # need "Select" of the group of the Variable
            # get the slice for this specific selection

            try:
                s = self._select_parent[dim]
            except KeyError:
                msg = ("'{dim}' is not a dimension of variable "
                       "'{name}', cannot select".format(dim=dim,
                                                        name=self.name))
                raise RuntimeError(msg)

            sel_elem.append(s[el])
        else:
            sel_elem.append(el)

    # select named arguments if necessary
    # (ignore named arguments not in dimensions)
    for i, dim in enumerate(self.dimensions):
        el = _dict.pop(dim, None)

        if el is not None:
            sel_elem[i] = self._select_parent[dim][el]

    # print unused arguments (-> not a dim of the var)
    for key in _dict:
        msg = ("Select: ignored named subsetting key: '{key}' "
               "(not a dimension of the variable)".format(key=key))
        print(msg)

    return tuple(sel_elem)

# ----------------------------------------------------------------------------

def coordinate_selection(getitem_func):

    @wraps(getitem_func)
    def wrap_getitem(self, elem):

        # add Ellipsis if elem has less members than ndim

        elem, _dict = __expand_elem__(self, elem)

        # find slices that have to be selected and select
        sel_elem = __parse_el__(self, elem, _dict)
        return getitem_func(self, sel_elem)

    return wrap_getitem



# ----------------------------------------------------------------------------

class Variable(netCDF4.Variable):

    """subclass netCDF4 to alter __getitem__"""

    def __init__(self, *arg, **kwargs):
        super(Variable, self).__init__(*arg, **kwargs)

        self.__dict__.update(self.__getattr__('__dict__'))
        # need to manually update __dict__
        self.__dict__['_select_parent'] = kwargs.pop('select_parent')

    @coordinate_selection
    def __getitem__(self, elem):
        return super(Variable, self).__getitem__(elem)

# ============================================================================


class _Variable(netCDF4._netCDF4._Variable):

    """subclass netCDF4 to alter __getitem__"""

    def __init__(self, *arg, **kwargs):
        self._select_parent = kwargs.pop('select_parent')
        super(_Variable, self).__init__(*arg, **kwargs)

    @coordinate_selection
    def __getitem__(self, elem):
        return super(_Variable, self).__getitem__(elem)

# ============================================================================


if __name__ == '__main__':

    fN = '/net/exo/landclim/mathause/cesm_data/f.e121.FC5.f19_g16.CTRL_2000-io384.001/lnd/hist/f.e121.FC5.f19_g16.CTRL_2000-io384.001.clm2.h0.0001-01.nc'

    ncf = Dataset(fN)

    #ncf = ncp.Dataset(fN)

    #print(ncf.variables['SOILLIQ'][Ellipsis, 1:3, {'lat' : (1, 3)}].shape)

    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.select['lat'][(3, 5)])
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.variables['SOILLIQ'][0, 5, slice(None), slice(None)].shape)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.variables['SOILLIQ'][0, 5].shape)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.variables['SOILLIQ'][:, [0, 5]].shape)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.variables['SOILLIQ'][:].shape)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.variables['SOILLIQ'][:].shape)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.variables['SOILLIQ'][0].shape)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.variables['SOILLIQ'][Ellipsis].shape)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.variables['SOILLIQ'][0, {0, 0.1}].shape)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.variables['SOILLIQ'][0, {0, 0.1}, {0, 30}, ...].shape)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.variables['SOILICE'][0, {0, 0.1}, {0, 30}, ...].shape)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.variables['SOILLIQ'][{0}].shape)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('??????????????')
    print(ncf.variables['lat'][
          {3}, {'lat': (5, 10), 'lat': (20, 30), 'aglkn': (1, 10)}])
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    # print(ncf.variables['lat'][{3}, 7, {'lat' : (5, 10)}])
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    fN = '/net/exo/landclim/mathause/cesm_data/f.e121.FC5.f19_g16.CTRL_2000-io384.001/lnd/hist/f.e121.FC5.f19_g16.CTRL_2000-io384.001.clm2.h0.0005-01.nc'
    ncf = Dataset(fN)

    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.variables['SOILLIQ'][0, {0, 0.1}, {0, 30}, ...].shape)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    fN = '/net/exo/landclim/mathause/cesm_data/f.e121.FC5.f19_g16.CTRL_2000-io384.001/lnd/hist/f.e121.FC5.f19_g16.CTRL_2000-io384.001.clm2.h0.000?-01.nc'
    ncf = MFDataset(fN)

    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.variables['SOILLIQ'][:, {0, 0.1}, {0, 30}, ...].shape)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    # print(ncf.variables['SOILLIQ'][{'lat' : (3, 15)}].shape)
    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    ncf = MSFDataset(fN)

    fN = '/home/mathause/Downloads/RawData_GHCNDEX_TXx_1951-2014_ANN_from-90to90_from-180to180.nc'
    ncf = Dataset(fN)

    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.variables['TXx'][:, {50, 60}, {35, 55}].shape)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(ncf.variables['TXx'][:, {'lat': (50, 60)}, {'lon': (35, 55)}].shape)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
