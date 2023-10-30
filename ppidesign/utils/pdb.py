import os
from collections import namedtuple
from typing import Dict, Iterable
from Bio import PDB, SeqIO
from Bio.pairwise2 import align
import numpy as np
from scipy.spatial import distance

from .logging import logging, warnings2logger


logger = logging.getLogger("stdout")


class PPIPdb:
    """Class wrapper that handles PDB functionalities

    Attributes:
        pdbfile : str
        
    Methods:
        get_strucuture : PDB.Structure.Structure
            Returns the structure in the pdb file.
        get_sequences(mode) : Dict[Bio.Seq.Seq]
            Returns all sequences in the pdb file.
    """

    def __init__(self, pdbfile: str):
        self.pdbfile = pdbfile

    @warnings2logger(logger) 
    def get_structure(self) -> PDB.Structure.Structure:
        """Access to the PDB structure"""
        fname = os.path.basename(self.pdbfile).split(".")[0]
        parser = PDB.PDBParser()        
        struct = parser.get_structure(fname, self.pdbfile)
        return struct
    
    @warnings2logger(logger) 
    def get_sequences(self, mode="pdb-seqres") -> Dict:
        """Extract sequences from the PDB
        
        Parameters:
            mode : str
                Sequence extraction mode: {pdb-seqres, pdb-atom}

        Returns:
            sequence : Dict[Seq]
                Dictionary of sequences by chain identifiers
        """
        sequences = {}
        for seq in SeqIO.parse(self.pdbfile, mode):
            chn = seq.id.split(":").pop()
            sequences[chn] = seq.seq
        return sequences

    def get_interface_residues(self, prime_chain: str, sec_chain: str|Iterable[str], *, cutoff=7., include_neighbors=False):
        """
        This function identifies residues on a primary chain that interact with
        residues on a secondary chain. An interaction is defined as less than 
        7 A Cbeta-Cbeta distance (Calpha if GLY).

        Parameters:
            prime_chain : str
                Chain identifier of the primary chain
            sec_chain : str or Iterable[str]
                Chain identifier or list of chain identifiers of
                a secondary chain
            cutoff : float
                Cutoff distance in Angstrom to define contacts
            include_neighbors : bool
                Sets whether neighbors of contact residues should 
                be considered contacts, too.

        Returns:
            contacs : NamedTuple
                seq : Seq
                    Reference sequence of the residues in primary chain
                is_contact: Array[bool]
                    Boolean array whether the corresponding residue is a contact
        """

        def extract_coords(chain):
            """Extracts the Cbeta coordinates (Gly: Calpha) from the chain."""
            crds = np.array([
                atom.coord for atom in chain.get_atoms()
                if atom.name == "CB" \
                    or (atom.name == "CA" and atom.parent.resname == "GLY")
            ])
            return crds

        coordsSec = np.zeros((0,3), dtype=np.float32)
        for chain in self.get_structure().get_chains():
            if chain.id == prime_chain:
                coordsPrm = extract_coords(chain)
            elif chain.id in sec_chain:
                coordsSec = np.concatenate([
                    coordsSec, extract_coords(chain)], axis=0)

        dist = distance.cdist(coordsPrm, coordsSec, metric="euclidean")
        contacts = (dist < cutoff).any(axis=1)
        if include_neighbors:
            contacts[1:] |= contacts[:-1]
            contacts[:-1] |= contacts[1:]

        seq = self.get_sequences("pdb-atom")
        Resobj = namedtuple("Contacts", ["seq", "is_contact"])
        result = Resobj(seq[prime_chain], contacts)
        return result