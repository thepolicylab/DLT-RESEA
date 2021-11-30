import decimal
import math
import warnings
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from decimal import Decimal, localcontext
from itertools import repeat
from pathlib import Path
from time import time
from typing import List, Optional, Union

import numpy as np
import pandas as pd
from tqdm.notebook import tqdm

from .config import get_global_config
from .types import FilenameType


def python_hash(SSN: int) -> int:
    """
    A pythonic implementation of COBOL code using floating-point arithmetic. Note that
    this will differ ever-so-slightly from the cobol_hash due to the differing rounding
    conventions.
    """
    # Constants determined by DoIT
    L_SD = SSN
    C_Q = 127773  # 3^2 * 14197
    C_A = 16807  # 7^5
    C_R = 2836  # 2^2 * 709
    C_M = 2147483647  # prime (In fact, 2^{2^5 - 1} - 1, double Mersenne)

    # Translated
    W_HI = L_SD // C_Q
    W_LO = L_SD % C_Q

    # Recombine the quotient and remainder mod a medium-sized almost-prime with two
    # coprime factors. (N.B. Not sure exactly why C_A is a power of 7 whereas C_R is
    # almost prime. Would be curious to read the history of this algorithm.)
    L_SD = C_A * W_LO - C_R * W_HI

    # Note that C_M is _almost_ 2^31, but not quite. Also, note that
    # C_A * W_LO - C_R * W_HI is maximized when SSN = C_Q - 1
    # and it is minimized when SSN is the largest social security number which is
    # exactly divisible by C_Q, i.e., (999_99_9999 // C_Q) * C_Q = 999_95_1498.
    #
    # In either case, C_A * W_LO - C_R * W_HI \in (-C_M, C_M) and so the following
    # block guarantees that L_SD will be in [0, C_M).
    #
    # We also note that the _smallest negative_ value that C_A * W_LO - C_R * W_HI can
    # achieve in theory is -1 (since C_A and C_R are coprime) but I haven't done the
    # computation to determine whether it's actually possible in this range of numbers
    if L_SD <= 0:
        warnings.warn("L_SD is negative")
        L_SD += C_M

    # And so by the above comment, L_RAND is in [0, 1) and this rounding gives us the
    # top 10 digits of the mantissa
    L_RAND = math.floor(L_SD / C_M * 1e10) / 1e10

    return L_RAND


def cobol_hash(SSN: int) -> float:
    """
    A python implementation of COBOL's fixed-point arithmetic
    """
    with localcontext() as ctx:
        # Constants determined by DoIT
        ctx.prec = 10
        ctx.rounding = decimal.ROUND_DOWN

        L_SD = Decimal(SSN)
        C_A = Decimal("0000016807")
        C_M = Decimal("2147483647")
        C_Q = Decimal("0000127773")
        C_R = Decimal("0000002836")

        # Translated
        W_HI = (L_SD / C_Q).quantize(Decimal("1E0"))  # L_SD // C_Q
        W_LO = L_SD - C_Q * W_HI  # L_SD % C_Q
        L_SD = C_A * W_LO - C_R * W_HI

        if L_SD <= 0:
            L_SD += C_M
        L_RAND = (L_SD / C_M).quantize(Decimal("1E-10"))

        if L_RAND == 0:
            warnings.warn("L_RAND is zero")
            L_SD += C_M

        return L_RAND


def generate_outcomes(
    input_list: Optional[List[int]] = None,
    process_type: str = "cobol",
    low: Optional[int] = None,
    high: Optional[int] = None,
    size: Optional[int] = None,
    all_values: Optional[bool] = False,
    generate_rand_whole: Optional[bool] = False,
) -> pd.DataFrame:
    """
    Helper function that generates L_RAND outcomes with the option for pythonic or cobol implmentations.
    """
    # Generate a random sample of SSNs to test, and sort to verify monotonicity of relationship
    if input_list is not None:
        ssn_pool = input_list
    elif not all_values:
        # Setting seed to ensure replicability
        np.random.seed(0)
        ssn_pool = np.random.randint(low=low, high=high, size=size)
        ssn_pool.sort()
    elif all_values:
        ssn_pool = np.arange(low, high)

    # apply random number generator to SSN pool
    if process_type == "python":
        with ThreadPoolExecutor() as executor:
            ssn_outcomes = list(
                tqdm(executor.map(python_hash, ssn_pool), total=len(ssn_pool))
            )

    if process_type == "cobol":
        with ThreadPoolExecutor() as executor:
            ssn_outcomes = list(
                tqdm(
                    executor.map(cobol_hash, ssn_pool.astype(str)), total=len(ssn_pool)
                )
            )

    df = pd.DataFrame(ssn_outcomes, columns=["L_RAND"])
    final_df = pd.concat([pd.Series(ssn_pool, name="SSN"), df], axis=1)
    if generate_rand_whole:
        final_df["L_RAND_WHOLE"] = final_df["L_RAND"] * 10_000_000_000

    return final_df


def chunk_using_generators(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def generate_all_L_RAND(
    filepath: Optional[FilenameType] = None,
    filename: FilenameType = "ssn_output.csv.gz",
    ssn_min: int = 1_01_0001,
    ssn_max: int = 899_99_9999,
    chunksize: int = 10_0000,
):
    """
    A function that calculates L_RAND values for all possible SSN from 001_01_0001 to 899_99_9999.
    This exercise was necessary to ensure that the maximum value attainable from all reasonable SSNs
    would result in an L_RAND value less than 9_999_999_999.
    """
    if filepath is None:
        # default to the DATA_DIR / reference
        filepath = Path(get_global_config().DATA_DIR) / "reference"

    # Total list of valid SSNs
    list_of_ssn = np.arange(ssn_min, ssn_max)
    # Divide the total list into manageable chunks
    list_of_list_of_ssn = list(chunk_using_generators(list_of_ssn, chunksize))
    # Process each list using COBOL
    with ProcessPoolExecutor() as executor:
        ssn_outcomes = list(
            tqdm(
                executor.map(generate_outcomes, list_of_list_of_ssn, repeat("cobol")),
                total=len(list_of_list_of_ssn),
            )
        )

    # Output data into a gzip dataframe.
    pd.DataFrame(pd.concat(ssn_outcomes)).sort_values(
        by="L_RAND", ascending=False
    ).reset_index(drop=True).to_csv(
        filepath / filename, compression="gzip", index=False
    )


def add_ms_to_seed(ssn: int, ms: int = None):
    """
    A good-enough solution to resolve local-randomization issues with the current DoIT algorithm.
    """
    if ms is None:
        ms = int(round(time(), 6) * 1e6) % 1_000_000
    return int(str(ssn + ms)[::-1])
