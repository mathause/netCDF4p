#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Author: Mathias Hauser
#Date: 





import netCDF4
import numpy as np

# SUBCLASS Dataset and Variable

# this is ugly, however we need to change the behaviour of Variable


        
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
    return slice(start, stop + 1, step)

        

class Select(object):
    """docstring for select"""
    def __init__(self, name, dimension, variable):
        super(Select, self).__init__()

        self.name = name
        self.dimension = dimension
        self.variable = variable
        self.selections = dict()

    
    def __getitem__(self, item):
        sel = self.selections.get(item, None)

        if sel is not None:
            return sel
        else:
            print('Selecting: {0}'.format(self.name))

            sel = _select(self, item)

            self.selections[item] = sel
            return sel



    def __setitem__(self, item, value):
        raise RuntimeError("Values can not be set manually")








def wherenearest(grid, pos):
    """return index nearest to pos"""
    val = np.abs(grid - pos)
    IDX = np.where(val == np.min(val))
    return IDX[0][0]





class Dataset(netCDF4.Dataset):
    """docstring for Dataset"""

    select = {}
    
    def __init__(self, *arg, **kwargs):

        try:
            super(Dataset, self).__init__(*arg, **kwargs)
        except RuntimeError:
            raise RuntimeError("No such file or directory '%s'" % arg[0])


        for v in self.variables.keys():
            ncv = self.variables[v]
            # unfortunately we have to subclass "variables" new in order to use the new version
            self.variables[v] = Variable(ncv.group(), ncv._name, ncv.datatype, ncv.dimensions, id=ncv._varid)


            self.select[v] = Select(v, self.dimensions.get(v, [None,]), self.variables.get(v, [None,]))





class Variable(netCDF4.Variable):
    """docstring for Variable"""
    def __init__(self, *arg, **kwargs):
        super(Variable, self).__init__(*arg, **kwargs)

    # use *elem to ensure that it is a tuple
    def __getitem__(self, elem, **kwargs):


        # parse elem: fill missing dims with Ellipsis



        if type(elem) is list:
            elem = (elem,)

        try: # could be only one entry of int, Ellipsis or slice
            missing_dim = self.ndim - len(elem)
        except TypeError:
            elem = (elem, )
            missing_dim = self.ndim - len(elem)

        if missing_dim > 0:
            if Ellipsis in elem:
                # find index of first occurence of Ellipsis
                i = next(el[0] for el in enumerate(elem) if el[1] == Ellipsis)
                # the first Ellipsis gets expanded
                elem = elem[:i+1] + (Ellipsis, ) * missing_dim + elem[i+1:]
            else:
                elem = elem + (Ellipsis, ) * missing_dim


            print("ELEM", elem)
            sel_elem = tuple()
            for i, el in enumerate(elem):

                if type(el) is set:

                    dim = self.dimensions[i]
                    print(dim)
                    sel_elem += (self.group().select[dim][el],)

                else:
                    sel_elem += (el, )



        print(sel_elem)

        print(elem)
        print(kwargs)
        print(self.shape)
        print(self.ndim)
        print(self._name)
        print(self.dimensions)
        
        

        #print(self._grp.get_selection('lat', {1, 5}))



        data = super(Variable, self).__getitem__(elem)

        print(data.shape)
        print('after')

        return data







fN = '/net/exo/landclim/mathause/cesm_data/f.e121.FC5.f19_g16.CTRL_2000-io384.001/lnd/hist/f.e121.FC5.f19_g16.CTRL_2000-io384.001.clm2.h0.0001-01.nc'



ncf = Dataset(fN)


# print(ncf.variables['SOILLIQ'][Ellipsis, 1:3, {'lat' : (1, 3)}].shape)


print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
#print(ncf.select['lat'][(3, 5)])
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print(ncf.variables['SOILLIQ'][(0, 5)].shape)
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print(ncf.variables['SOILLIQ'][0, 5].shape)
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print(ncf.variables['SOILLIQ'][[0, 5]].shape)
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print(ncf.variables['SOILLIQ'][:, ...].shape)
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print(ncf.variables['SOILLIQ'][:].shape)
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print(ncf.variables['SOILLIQ'][0].shape)
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print(ncf.variables['SOILLIQ'][Ellipsis].shape)
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
