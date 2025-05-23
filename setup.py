from setuptools import setup, find_packages

setup(
    name="apigee-opdk-saas-installer",
    version="1.0.0",
    description="A Python-based tool for installing and managing Apigee resources across different environments and instance types (OPDK and SaaS)",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "pyyaml>=5.4.1",
        "python-dotenv>=0.19.0"
    ],
    entry_points={
        'console_scripts': [
            'apigee-installer=install.ApigeeInstaller:main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
