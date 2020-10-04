from setuptools import setup
from sys import version_info

def get_version(rel_path):
    for line in open(rel_path).readlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

VERSION=get_version("citizenshell/__init__.py")

REQUIREMENTS = [
    'termcolor>=1.1.0',
    'paramiko>=2.4.0',
    'uritools>=2.1.0',
    'pyserial>=3.4',
    'scp>=0.10.2',
    'backports.tempfile>=0.4.0'
]

if version_info.major == 2:
    REQUIREMENTS += [
        'bcrypt==3.1.7'
    ]

setup(
    name='citizenshell',
    version=VERSION,
    packages=['citizenshell'],
    package_data={ "citizenshell": [ "VERSION" ]},
    url='https://github.com/meuter/citizenshell',
    license='MIT',
    author='Cedric Meuter',
    author_email='cedric.meuter@gmail.com',
    description='Interact with shell locally or over different connection types (telnet, ssh, serial, adb)',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords=["shell", "telnet", "adb", "ssh", "serial"],
    download_url="https://github.com/meuter/citizenshell/archive/" + VERSION + ".tar.gz",
    install_requires=[
        'termcolor>=1.1.0',
        'paramiko>=2.4.0',
        'uritools>=2.1.0',
        'pyserial>=3.4',
        'scp>=0.10.2',
        'backports.tempfile>=0.4.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities',
    ],
)
