from decimal import Decimal

import numpy as np
import pytest

from dlt import randomizer_utils as ran


@pytest.fixture(scope="function")
def random() -> np.random.Generator:
    return np.random.default_rng(123456)


def test_python_hash():
    """
    Examine the basic functionalities of python_hash
    """
    input_ssn = 123_456_789
    expected_L_RAND = 0.2184182969

    assert ran.python_hash(input_ssn) == expected_L_RAND


def test_cobol_hash():
    """
    Examine the basic functionalities of cobol_hash
    """
    input_ssn = 123_456_789
    expected_L_RAND = Decimal("0.2184182969")

    assert ran.cobol_hash(input_ssn) == expected_L_RAND


def test_generate_outcomes():
    """
    Verify the outcomes generated by the cobol algorithm and python algorithm are equal to each other within an absolute range of 1.
    """
    cobol_df = ran.generate_outcomes(
        low=0, high=999_999_999, size=10, process_type="cobol", generate_rand_whole=True
    )

    python_df = ran.generate_outcomes(
        low=0,
        high=999_999_999,
        size=10,
        process_type="python",
        generate_rand_whole=True,
    )

    assert cobol_df.shape == python_df.shape
    np.testing.assert_allclose(
        actual=cobol_df.L_RAND_WHOLE.astype("float64"),
        desired=python_df.L_RAND_WHOLE,
        atol=1,
    )


def test_add_ms_to_seed():
    """
    Ensure that the behavior of adding microseconds is as expected
    """
    input_ssn = np.random.randint(low=1_01_0001, high=999_999_999, size=10)
    rev_input_ssn = [str(ssn)[::-1] for ssn in input_ssn]
    new_seed = [str(ran.add_ms_to_seed(ssn)) for ssn in input_ssn]

    # because we are adding a 6 digit microsecond, the last 3 digits of the new_seed
    # and the first three of the input_ssn should be within a very small range (due to rounding errors)
    np.testing.assert_allclose(
        actual=[int(rev_ssn[-3:][::-1]) for rev_ssn in rev_input_ssn],
        desired=[int(seed[-3:][::-1]) for seed in new_seed],
        atol=2,
    )
