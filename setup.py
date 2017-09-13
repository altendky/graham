import setuptools


setuptools.setup(
    name='graham',
    use_scm_version=True,
    description='Graham, bringing together attrs and marshmallow.',
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
    setup_requires=[
        'setuptools_scm',
    ],
)
