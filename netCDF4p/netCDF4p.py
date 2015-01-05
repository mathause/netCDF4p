#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Author: Mathias Hauser
#Date: 14.12.2014

import netCDF4
import numpy as np
from glob import glob

from collections import OrderedDict
# SUBCLASS Dataset and Variable
# ---------------------------------------------------------------------------


def _select(self, item):

    if len(item) > 3:
        raise IndexError("selector for dimension %i (%s) has \
            too many elements" % ("XXXX", "XXX"))

    data = self.variable[:]

    if data is None:
        raise RuntimeError("dimension XYZ has no data")

    start = wherenearest(data, item[0])
    stop = start if len(item) < 2 else wherenearest(data, item[1])
    step = 1 if len(item) < 3 else item[2]

    # reverse start stop if dimen is sorted the other way round
    if start > stop:
        start, stop = stop, start
    # python slice notation: stop is the first that is NOT selected
    sel = slice(start, stop + 1, step)

    vals = data[sel]
    verbose(self.name, item, vals[0], stop_val=vals[-1])
    return sel

# ---------------------------------------------------------------------------


def verbose(name, item, start_val, stop_val):
    """print item and resulting selection"""
    string = "Select '{0}': ".format(name)

    if len(item) == 1:
        msg = "{0}{1} selects: {2:5.3f}".format(string, item[0], start_val)
    elif len(item) == 2:
        msg = "{0}{1}...{2} selects: {3:5.3f}...{4:5.3f}".format(string,
         item[0], item[1], start_val, stop_val)

    print(msg)

# ============================================================================

class Select(object):
    """docstring for select"""
    def __init__(self, name, dimension, variable):
        super(Select, self).__init__()

        self.name = name
        self.dimension = dimension
        self.variable = variable

        # se
        self.selections = OrderedDict()

    
    def __getitem__(self, item):
        # check if this particular case was already selected
        sel = self.selections.get(item, None)

        if sel is not None:
            return sel
        else:
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

        try:
            super(Dataset, self).__init__(*arg, **kwargs)
        except RuntimeError:
            raise RuntimeError("No such file or directory '%s'" % arg[0])

        select = kwargs.pop('select', None)
        if select is None:
            self.__dict__['select'] = OrderedDict()
        else:
            self.__dict__['select'] = select

        for var in self.variables.keys():
            ncv = self.variables[var]
            # unfortunately we have to reassign "variables" in order to
            # use the new version
            self.variables[var] = Variable(ncv.group(),
                                           ncv._name,
                                           ncv.datatype,
                                           ncv.dimensions,
                                           id=ncv._varid,
                                           select_parent=self.select
                                           )

            # add the new Select class to the Dataset
            self.select[var] = Select(var,
                                      self.dimensions.get(var, [None]),
                                      self.variables.get(var, [None])
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


        self.__dict__['select'] = OrderedDict()

        for var in self.variables.keys():
            ncv = self.variables[var]
            # unfortunately we have to reassign "variables" in order to
            # use the new version

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
            self.select[var] = Select(var,
                                      self.dimensions.get(var, [None]),
                                      self.variables.get(var, [None])
                                      )

# # ============================================================================


class MSFDataset(object):
    """docstring for MSFDataset"""
    def __init__(self, files, check=False, aggdim=None, exclude=[]):
        super(MSFDataset, self).__init__()
        
        # Open the master file in the base class, so that the CDFMF instance
        # can be used like a CDF instance.
        if isinstance(files, str):
            if files.startswith('http'):
                msg='cannot using file globbing for remote (OPeNDAP) datasets'
                raise ValueError(msg)
            else:
                files = sorted(glob(files))







        master = files[0]
        print(master)
        print(files)
        
        cdfm = Dataset(master)
        # copy attributes from master.
        for name, value in cdfm.__dict__.items():
            self.__dict__[name] = value
        


        self._files = files





        ncfs = []
        for _file in files[2:]:
            ncfs.append(Dataset(_file, select=self.select))

        self._ncfs = ncfs


    def __getitem__(self, key):
        return self._ncfs[key]

    def __iter__(self):
        return self._ncfs.__iter__()

    def __len__(self):
        return self._ncfs.__len__()


# ============================================================================



# subclass netCDF4.Variable to alter __getitem__

def __expand_elem__(elem, ndim):
    """parse the slice input"""

    # PARSE ELEM
    # we need to be sure of the position of all elem

    # (1) only 1 elem is given 
    if not isinstance(elem, tuple):
        elem = (elem, )
    # if type(elem) is list or isinstance(elem, set):
    #     elem = (elem,)

    # if not np.iterable(elem):
    #     elem = (elem, )


    # search for named elements (dicts)
    had_dict = False

    _elem = ()
    _dict = dict()

    for i, el in enumerate(elem):
        if isinstance(el, dict):
            had_dict = True

            for key in el.keys():
                _dict[key] = el[key]

        elif had_dict:
            raise KeyError('dict argument can not be followed by positional argument')

        else:
            _elem = _elem + (el, )


    elem = _elem

    # (2) make sure there are not too many dimensions in slice.
    if len(elem) > ndim:
        raise ValueError("slicing expression exceeds the number of dimensions \
            of the variable")

    # (2) if less elements are given then there are dimensions:
    #     fill them with Ellipsis

    missing_dim = ndim - len(elem)

    if missing_dim > 0:
        # the first occurence of Ellipsis gets expanded
        if Ellipsis in elem:
            # first occurence of Ellipsis
            i = next(el[0] for el in enumerate(elem) if el[1] == Ellipsis)
            # expand
            elem = elem[:i+1] + (slice(None), ) * missing_dim + elem[i+1:]
        else:
            elem = elem + (slice(None), ) * missing_dim


    return elem, _dict

# ----------------------------------------------------------------------------

def __parse_el__(self, elem, _dict):
    """find slices that have to be selected"""

    sel_elem = list()


    for i, el in enumerate(elem):

        # coordinate subsetting happens for sets
        if isinstance(el, set):
            # convert to tuple (must be hashable)
            el = tuple(el)

            if len(el) != 2 and len(el) != 1:
                raise IndexError("Length of coordinate subsetting must be 1 or 2")

            # name of the dimension
            dim = self.dimensions[i]

            # need "Select" of the parent of the Variable
            # get the slice for this specific selection
            sel_elem.append(self._select_parent[dim][el])
        else:
            sel_elem.append(el)



        for i, dim in enumerate(self.dimensions):
            el = _dict.pop(dim, None)

            if el is not None:
                sel_elem[i] = self._select_parent[dim][el]



        for key in _dict:
            print('ignored key: {key}'.format(key=key))


    return tuple(sel_elem)

# ----------------------------------------------------------------------------


class Variable(netCDF4.Variable):
    """subclass netCDF4 to alter __getitem__"""
    def __init__(self, *arg, **kwargs):
        super(Variable, self).__init__(*arg, **kwargs)
        self.__dict__['_select_parent'] = kwargs.pop('select_parent')

    def __getitem__(self, elem):

        # add Ellipsis if elem has less members than ndim
        elem, _dict = __expand_elem__(elem, self.ndim)

        # find slices that have to be selected and select
        sel_elem = __parse_el__(self, elem, _dict)

        data = super(Variable, self).__getitem__(sel_elem)

        return data


# ============================================================================

class _Variable(netCDF4._Variable):
    """subclass netCDF4 to alter __getitem__"""

    def __init__(self, *arg, **kwargs):
        self._select_parent = kwargs.pop('select_parent')
        super(_Variable, self).__init__(*arg, **kwargs)


    def __getitem__(self, elem):

        # add Ellipsis if elem has less members than ndim
        elem, _dict = __expand_elem__(elem, self.ndim)

        # find slices that have to be selected and select
        sel_elem = __parse_el__(self, elem, _dict)

        data = super(_Variable, self).__getitem__(sel_elem)

        return data


# ============================================================================


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
print(ncf.variables['lat'][{3}, {'lat' : (5, 10), 'lat' : (20, 30), 'aglkn' : (1, 10)}])
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