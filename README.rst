netCDF4p
========

Wrapper around python-netCDF4 that allows Coordinate subscripting, similar to NCL.

It has the full capability of python-netCDF4 *plus* allows coordinate subsetting. This is how you use it::

    import netCDF4p as ncp
    # open netCDF file
    ncf = nc.Dataset('file.nc')
    # given the variable Temperature has the dimensions | time x lat x lon |
    # you can select a region that conforms to 0° to 30°N and 0° to 20° E like so:
    ncf.variables['Temperature'][:, {0, 30}, {0, 20}]
    # coordinate selections can also be made passing a dict ('named argument')
    ncf.variables['Temperature'][:, {'lat' : (0, 30), 'lon' : (0, 20)}]

Features
--------

- Everything netCDF4 allows
- Coordinate subsetting by positional argument.
- Coordinate subsetting by named (dict) argument.

Installation
------------

Not published on PyPy (yet). Install netCDF4p directly from GitHub:

    pip install git+git://github.com/mathause/netCDF4p.git


Contribute
----------

- Issue Tracker: github.com/mathause/netCDF4p/issues
- Source Code: github.com/mathause/netCDF4p

Support
-------

If you are having issues, please let us know.
Please use the Issue Tracker: github.com/mathause/netCDF4p/issues


License
-------

The project is licensed under the MIT license.

