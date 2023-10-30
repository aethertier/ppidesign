"""
This module holds a class that defines the target interface of the 
protein-protein interface design task.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class PPITarget:
    """
    Namespace for the optimization task.

    Attributes:
        pdbfile : str
            Filepath with the input PDB on which the optimization is based.
        primary_chain : str
            Chain identifier of the protein to be modified.
        secondary_chains : str or Tuple(str)
            Chain identifiers of proteins that define the interface towards
            `target_chain`
    """
    pdbfile : str
    primary_chain : str
    secondary_chains : Tuple[str]
