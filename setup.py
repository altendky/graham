import setuptools


setuptools.setup(
    name='graham',
    use_scm_version={'version_scheme': 'post-release'},
    description="Graham, making s'mores with attrs and marshmallow.",
    author='Kyle Altendorf',
    author_email='sda@fstab.net',
    url='https://github.com/altendky/graham',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'attrs',
        'marshmallow',
    ],
    extras_require={
        'docs': [
            'sphinx',
            'sphinx-issues'
        ],
        'tests': [
            'codecov',
            'pytest',
            'pytest-cov',
            'tox',
        ],
    },
    setup_requires=[
        'setuptools_scm',
    ],
)
