from setuptools import setup

setup(
    name='xtralien',
    version='1.3.0',
    description='A connector to implement connecting to CLOI-based instruments',
    author='Xtralien',
    author_email='jack@xtralien.com',
    url='https://github.com/xtralien/pyxtralien.git',
    packages=['xtralien'],
    extras_require={
        'Serial': ['pyserial']
    },
    scripts=['bin/list_xtraliens'],
    license='GPLv3'
)
