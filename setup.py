from os.path import abspath, dirname, join

from setuptools import find_packages, setup

basedir = abspath(dirname(__file__))

with open(join(basedir, 'README.md')) as f:
    README = f.read()

setup(
    name='gsppy',
    version='2.0.0',
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
    python_requires='>=3.11',
    install_requires=[
        # No additional runtime dependencies are required since the project uses standard library modules only.
    ],
    extras_require={
        'dev': [
            'pylint==3.2.6',
            'pytest==8.3.4',
            'pytest-benchmark==5.1.0',
            'pytest-cov==6.0.0',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: English'
    ],
    keywords='GSP, sequential patterns, data analysis, sequence mining',
    entry_points={
        'console_scripts': [
            'gsppy = gsppy.cli:main',
        ],
    },
    tests_require=['pytest'],
    test_suite='gsppy.tests',
)
