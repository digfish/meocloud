from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="meocloud-repl",
    version="0.0.1",
    author="Rui Rascasso",
    author_email="rascasso@digfish.org",
    description="A REPL tool for Meo Cloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/digfish/meocloud",
    packages=find_packages(exclude=['tests*','my_tests*']),
    install_requires=[
        'click>=7.1.2',
        'requests>=2.25.0',
        'requests-oauthlib>=1.3.0',
        'pyreadline3>=3.4.1'
    ],
    entry_points={
        'console_scripts': [
            'meocloud = meocloud.cli:main',
            'meocloudrepl = meocloud.repl:main'
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)