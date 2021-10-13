from setuptools import setup

setup(
    name='pythclient',
    version='0.0.1',
    packages=['pythclient'],
    author='Pyth Developers',
    author_email='contact@pyth.network',
    install_requires=['aiodns', 'aiohttp', 'backoff', 'base58', 'loguru']
)
