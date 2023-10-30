from tempfile import NamedTemporaryFile
import numpy as np
import pandas as pd
from b2bTools import SingleSeq
from ..utils.logging import logging, stdout2logger


logger = logging.getLogger("stdout")


class B2BWrapper:
    """A wrapper to run b2bTools"""

    PREDICTORS = ["dynamine", "disomine"]
    RESULT_LABELS = [
        ("SEQ", "seq"), ("dynamics", "backbone"), ("disorder", "disoMine"),
        ("helix", "helix"), ("sheet", "sheet"), ("ppII", "ppII"), ("coil", "coil")
    ]

    @stdout2logger(logger)
    def run_predictions(self, *sequences) -> pd.DataFrame:
        """Run b2bTools on the given set of sequences"""
        with NamedTemporaryFile(mode="w", suffix=".fasta") as tmpf:
            # Write a fasta file with the sequences
            for i, seq in enumerate(map(str, sequences)):
                tmpf.write(f">Seq{i:05d}\n")
                tmpf.write("\n".join([seq[i:i+60] for i in range(0, len(seq), 60)]) + "\n")
            tmpf.flush()

            # Run predictions
            b2b = SingleSeq(tmpf.name)
            b2b.predict(tools=self.PREDICTORS)
            results = b2b.get_all_predictions()
            dflist = np.zeros(len(sequences), dtype=object)
            for label, data in results.items():
                i = int(label[3:])
                dflist[i] = pd.DataFrame({
                    key: data[col] for key, col in self.RESULT_LABELS
                })
            return dflist