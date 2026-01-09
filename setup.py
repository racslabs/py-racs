from setuptools import setup, find_packages

setup(
    name="racs",
    version="0.1.2",
    packages=find_packages(),
    install_requires=["msgpack", "crc32c", "mmh3", "zstd"],
    description="Python client library for RACS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)