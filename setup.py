from setuptools import setup

setup(name='netCDF4p',
    version='0.9',
    description='Addition to netCDF4 to select by dimension',
    url='',
    author='Mathias Hauser',
    author_email='mathias.hauser@env.ethz.ch',
    license='MIT',
    packages=['netCDF4p'],
    install_requires=[
        'netCDF4',
		'numpy',
		],
    zip_safe=False)







