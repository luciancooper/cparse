from setuptools import setup,find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='cparse',
    version='0.0.2',
    author='Lucian Cooper',
    author_email='cooperlucian@gmail.com',
    url='https://github.com/luciancooper/cparse',
    project_urls={
        "Documentation": "https://cparse.readthedocs.io",
    },
    description='Code parser tool',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='parser',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Operating System :: MacOS',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
    install_requires=['pydecorator'],
    entry_points={
        'console_scripts': [
            'cparse = cparse.__main__:main',
        ]
    },
)
