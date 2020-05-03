from os.path import abspath, dirname, join

from setuptools import find_packages, setup

basedir = abspath(dirname(__file__))

with open(join(basedir, 'README.md')) as f:
    README = f.read()

setup(
    name='gsppy',
    version='1.1',
    description='GSP (Generalized Sequence Pattern) algorithm in Python',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Jackson Antonio do Prado Lima',
    author_email='jacksonpradolima@gmail.com',
    maintainer='Jackson Antonio do Prado Lima',
    maintainer_email='jacksonpradolima@gmail.com',
    license='MIT',
    url='https://github.com/jacksonpradolima/gsp-py',
    packages=find_packages(exclude=['test_']),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        "Operating System :: OS Independent",
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
    ],
    install_requires=[],
)