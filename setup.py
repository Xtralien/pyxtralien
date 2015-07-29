from setuptools import setup

setup(
    name='cloi',
    version='0.0.4',
    description='A connector to implement connecting to CLOI-based instruments',
    author='Xtralien',
    author_email='jack@xtralien.com',
    url='https://github.com/xtralien/pycloi.git',
    packages=['cloi'],
    install_requires=['pyserial', 'netifaces'],
    license='GPLv3'
)
