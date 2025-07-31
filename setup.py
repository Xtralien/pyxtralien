from setuptools import find_packages, setup

try:
    with open('README.md') as f:
        long_description = f.read()
except:
    long_description = ''

setup(
    name='xtralien',
    version='2.11.1',
    description='A library for controlling Ossila\'s Source Measure Unit',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ossila Ltd.',
    author_email='info@ossila.com',
    url='https://github.com/xtralien/pyxtralien.git',
    packages=find_packages(where='src', exclude=['additional']),
    package_dir={'': 'src'},
    python_requires='>=3.5',
    extras_require={
        'numpy': ['numpy'],
        'Serial': ['pyserial'],
        'keithley': ['pyVISA'],
        'prompt': ['pyreadline', 'scipy', 'matplotlib', 'ipython']
    },
    license='MIT'
)
