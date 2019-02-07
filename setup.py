from setuptools import setup,find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='cparse',
    version='0.0.1',
    author='Lucian Cooper',
    url='https://github.com/luciancooper/cparse',
    description='Code parser',
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
        'Operating System :: Microsoft :: Windows',
    ],
    packages=find_packages(),
    install_requires=['pydecorator'],
    entry_points={
        'console_scripts': [
            'cparse = cparse.__main__:main',
        ]
    },
)
