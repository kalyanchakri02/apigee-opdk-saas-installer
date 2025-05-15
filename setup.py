from setuptools import setup, find_packages

setup(
    name="apigee-opdk-saas-installer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'requests>=2.31.0',
        'pyyaml>=6.0.1',
    ],
)
