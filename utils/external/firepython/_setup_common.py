import firepython


SETUP_ARGS = dict(
    name='FirePython',
    version=firepython.__version__,
    description='Python logging console integrated into Firebug',
    long_description=firepython.__doc__,
    author='Antonin Hildebrand',
    author_email='antonin@hildebrand.cz',
    url='http://firelogger.binaryage.com',
    packages=['firepython'],
    py_modules=['gprof2dot'], #XXX remove when easy_install-able
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Logging',
    ],
    install_requires=['jsonpickle'],
    license='BSD',
    platforms=['any'],
    test_suite='nose.collector',
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'firepython-demo-app = firepython.demo:main',
            'firepython-graphviz = firepython.mini_graphviz:main',
        ],
        'paste.filter_factory': [
            'main = firepython.middleware:paste_filter_factory',
        ],
        'paste.filter_factory': [
            'main = firepython.middleware:paste_filter_factory',
        ],
    }
)
