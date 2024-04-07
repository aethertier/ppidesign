# ppidesign: A pipeline tool to design protein-protein interfaces

* Author: David Bickel
* Date: 10/30/2023

## Installation

1. Install miniconda or anaconda on your local machine

2. Create virtual evironment and activate

```sh
conda create -n ppidesign python=3.10
conda activate ppidesign
```

3. Install AmberTools trough conda

```sh
conda install -c conda-forge ambertools=23
```

4. Download, build, and install this repository

```sh
git clone https://github.com/aethertier/ppidesign.git
cd ppidesign
make build
make install
```

## Usage

For the usage of the package, consult the examples notebook [here](./examples/examples.ipynb).
