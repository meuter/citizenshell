from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


setup(
    name='citizenshell',
    version='0.3.5',
    packages=['citizenshell'],
    url='https://github.com/meuter/citizenshell',
    license='MIT',
    author='Cedric Meuter',
    author_email='cedric.meuter@gmail.com',
    description='Interact with shell locally or over different connection types (telnet, ssh, serial, adb)',
    long_description=long_description,
    keywords=["shell", "telnet", "adb", "ssh", "serial"],
    classifiers=[],
    download_url="https://github.com/meuter/citizenshell/archive/0.3.5.tar.gz",
    install_requires=[
        'termcolor>=1.1.0',
        'paramiko>=2.4.0'
    ]
)
