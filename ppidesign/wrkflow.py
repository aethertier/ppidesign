from Bio.pairwise2 import align
from .utils.ppitarget import PPITarget
from .utils.pdb import PPIPdb
from .b2bopt import B2BWrapper, B2BEvolver


class PPIWorkflow:
    
    def __init__(self, positive: PPITarget, negative: PPITarget):
        """
        Initialize the workflow.

        Parameters:
        -----------
            positive : PPITarget
                The protein-protein interaction that is to be promoted.
            negative : PPITarget
                The protein-protein interaction that is to be abrogated.
        """
        self.posPdb = PPIPdb(positive.pdbfile)
        self.posChain = positive.primary_chain
        self.posInterfaceChains = positive.secondary_chains
        self.negPdb = PPIPdb(negative.pdbfile)
        self.negChain = negative.primary_chain
        self.negInterfaceChains = negative.secondary_chains
        self.result = None

    def run(self, popsize: int = 8, maxiter: int = 10, mutation: float = .08,
            recombination: float = .5, **kwargs):
        """ Run the optimization workflow to abrogate the interface in negPdb,
        while retaining the interface in posPdb. The protein design is performed
        by a genetic algorithm.

        Parameters:
        -----------
            popsize : int
                Population size factor for the genetic algorithm. The final 
                population size will be `no. substitution sites * popsize`
            maxiter : int
                Maximum number of iterations to beused to optimize. Does not 
                directly correlate to the number of function evaluations.
            mutation : float
                Mutation rate as a value in the range [0., 1.)
            recombination : float
                Recombination rate as a value in the range [0., 1.)
            
        Returns:
        --------
            result : NamedTuple
                The result object of the optimmization with two attributes. 
                The attribute `seq` contains the optimized sequence, while the 
                `score` attribute is a measure of the biophysical distance between
                the wt and the optimized sequence.
        """
        # Clear any previous results
        self.result = None
        # Identify residues in the interface that are exclusive to the
        # complext that should be abrogated
        sequence, subst_maks = self.get_nonoverlapping_interface()
        subst_positions = [i for i, b in enumerate(subst_maks) if b]
        # Run genetic optimization algorithm to optimize sequence
        # (This is a very naive implementation, as as PoC only)
        evolver = B2BEvolver(sequence, subst_positions)
        self.result = evolver.optimize(
                        popsize = popsize, 
                        maxiter = maxiter, 
                        mutation = mutation, 
                        recombination = recombination, 
                        **kwargs)
        return self.result

    def get_nonoverlapping_interface(self):
        """This function identifies interface residues in negPdb, that are not
        part of the interface in posPdb.
        
        Returns:
        --------
            seq : Seq
                The resseq sequence of negPdb
            msk : Array[bool]
                Boolean values for each residue if it is part of the interface.
        """
        posSeq, posMsk = self.posPdb.get_interface_residues(self.posChain, 
                                                            self.posInterfaceChains,
                                                            include_neighbors=True)
        negSeq, negMsk = self.negPdb.get_interface_residues(self.negChain, 
                                                            self.negInterfaceChains,
                                                            include_neighbors=True)
        # Find residues that interact in negPdb but not in posPdb
        # To account for potential missing residues, use alignment
        aln = align.globalms(posSeq, negSeq, 1, -10, -1, 0,
                    penalize_end_gaps= False, one_alignment_only=True).pop()
        posIter, negIter = (p for p in posMsk), (n for n in negMsk)
        non_overlapping_interface = []
        for pos,neg in zip(aln.seqA, aln.seqB):
            if neg != "-":
                negInterface = next(negIter)
                posInterfce = next(posIter) if pos != "-" else False
            elif pos != "-":
                next(posIter)
            non_overlapping_interface.append(
                negInterface & (negInterface ^ posInterfce))
        return negSeq, non_overlapping_interface
    
    def get_b2b_prediction(self, *sequences):
        b2b = B2BWrapper()
        return b2b.run_predictions(*sequences)
    

        