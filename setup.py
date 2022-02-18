from setuptools import setup

requirements = ['aiodns', 'aiohttp>=3.7.4', 'backoff', 'base58', 'dnspython', 'flake8', 'loguru', 'typing-extensions']

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='pythclient',
    version='0.1.0',
    packages=['pythclient'],
    author='Pyth Developers',
    author_email='contact@pyth.network',
    description='A library to retrieve Pyth account structures off the Solana blockchain.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pyth-network/pyth-client-py',
    project_urls={
        'Bug Tracker': 'https://github.com/pyth-network/pyth-client-py/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    install_requires=requirements,
    extras_require={
        'testing': requirements + ['mock', 'pytest', 'pytest-cov', 'pytest-socket',
                                   'pytest-mock', 'pytest-asyncio'],
    },
    python_requires='>=3.7.0',
)
