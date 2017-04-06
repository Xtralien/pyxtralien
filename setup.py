from setuptools import setup

try:
    with open('README.md') as f:
        long_description = f.read()
except:
    long_description = ''

setup(
    name='xtralien',
    version='2.9.0',
    description='A connector to implement connecting to CLOI-based instruments',
    long_description=long_description,
    author='Xtralien',
    author_email='jack@xtralien.com',
    url='https://github.com/xtralien/pyxtralien.git',
    packages=['xtralien'],
    extras_require={
        'Serial': ['pyserial'],
        'keithley': ['pyVISA'],
        'prompt': ['pyreadline']
    },
    license='GPLv3'
)
