from setuptools import setup

setup(
    name='cloi',
    version='0.4.7',
    description='A connector to implement connecting to CLOI-based instruments',
    author='Xtralien',
    author_email='jack@xtralien.com',
    url='https://github.com/xtralien/pycloi.git',
    packages=['cloi'],
    extras_require={
        'Serial': ['pyserial'],
        'Netscan': ['netifaces']
    },
    license='GPLv3'
)
