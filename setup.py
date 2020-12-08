from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="meocloud",
    version="0.0.2",
    author="Igor Dantas de Aguiar",
    author_email="igordantas91@icloud.com",
    description="unofficial meocloud package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/IgorDantasID/meocloud",
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'click>=7.1.2',
        'requests>=2.25.0',
        'requests-oauthlib>=1.3.0',
    ],
    entry_points={
        'console_scripts': [
            'meocloud = meocloud.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)