from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="ppidesign",
    packages=["ppidesign"],
    version="0.0.1b2",
    author="David Bickel",
    description="Tool for modulating protein-protein interfaces",
    license="OSI Approved :: GNU General Public License v3 (GPLv3)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    maintainer="David Bickel",
    url="",
    include_package_data=True,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha"
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics"
    ],
    python_requires=">=3.10,<3.11",
    install_requires=requirements,
)
