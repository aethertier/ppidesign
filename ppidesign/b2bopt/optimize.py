from collections import namedtuple
from typing import Callable, Iterable, NamedTuple
import numpy as np
from scipy.optimize import differential_evolution
import tqdm
from .b2bwrapper import B2BWrapper


class B2BEvolver:
    """This class implements a genetic algorithm to evolve a sequence
    to be as divergent as possible from a reference sequence."""

    AMINO_ACIDS = np.fromiter("ACDEFGHIKLMNPQRSTVWY", dtype="U1")

    def __init__(self, ref_sequence, substitution_positions):
        self.ref_sequence = np.fromiter(ref_sequence, dtype="U1")
        self.ref_data = self._get_ref_data()
        self.positions = substitution_positions

    def optimize(self,
            func: Callable = None,
            bounds: Iterable = None,
            args: Iterable = None,
            popsize: int = 8,
            maxiter: int = 10,
            mutation: float = .08,
            recombination: float = .2,
            **kwargs) -> NamedTuple:
        
        with tqdm.tqdm(total=maxiter*popsize*popsize*len(self.positions)) as pbar:
            result = differential_evolution(
                func = func or self.evaluate_fitness,
                bounds = bounds or [(0., 20. - 1e-6)] * len(self.positions),
                args = args or (pbar,), 
                popsize = popsize, 
                maxiter = maxiter,
                mutation = mutation,
                recombination = recombination,
                **kwargs
            )
        ResultObj = namedtuple("Result", ["seq", "score"])
        res = ResultObj(
            seq = self.get_substituted_sequence(result.x),
            score = result.fun)
        return res

    def evaluate_fitness(self, params, pbar=None):
        sequence = self.get_substituted_sequence(params)
        result = B2BWrapper().run_predictions(sequence)[0]
        score = np.sum((self.ref_data - result.iloc[:,1:].to_numpy()) ** 2)
        if pbar is not None:
            pbar.update(1)
        return -1 * score

    def _get_ref_data(self):
        b2b = B2BWrapper()
        df = b2b.run_predictions("".join(self.ref_sequence))[0]
        return df.iloc[:,1:].to_numpy()

    def get_substituted_sequence(self, params):
        subst = self.AMINO_ACIDS[np.floor(params).astype(int)]
        sequence = self.ref_sequence.copy()
        sequence[self.positions] = subst
        return "".join(sequence)
