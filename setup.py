import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'django==1.11.3',
    'django-filter==1.0.4',
    'django-guardian==1.4.9',
    'django-debug-toolbar==1.8',
    'django-compressor==2.1.1',
    'django-webpack-loader==0.5.0',
    'djangorestframework==3.6.3',
    'dj-static==0.0.6',
    'factory_boy==2.8.1',
    'appdirs==1.4.3',
    'typing==3.6.1',
    'dictdiffer==0.6.1',
    'jsonschema==2.6.0',
    'click==6.7',
    'gunicorn==19.7.1',
]

setup(
    name='configfactory',
    version='1.0dev',
    description='ConfigFactory',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Framework :: Django",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Anton Ruhlov',
    author_email='antonruhlov@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'tests': requires + [
            'pytest',
            'pytest-django',
        ],
    },
    install_requires=requires,
    entry_points="""\
    [console_scripts]
    configfactory = configfactory.cli:main
    """,
)
