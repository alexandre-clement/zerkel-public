from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

setup(
    name='Zerkel',
    version='2019.09.11',
    url='https://github.com/alexandre-clement/zerkel',
    author='Alexandre Clement',
    author_email='alexandre.clement@unice.fr',
    description='Primitive recursive programming on pure sets.',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    python_requires='>=3.6.*',
    install_requires=[
        'matplotlib==3.1.0',
        'numpy==1.16.3',
        'pyparsing==2.4.0',
        'tabulate==0.8.3'
    ]
)
