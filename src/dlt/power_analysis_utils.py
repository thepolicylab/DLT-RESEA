from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd


def _convert_seed_to_randomstate(
    seed: Optional[Union[int, np.random.mtrand.RandomState]]
) -> np.random.mtrand.RandomState:
    if not seed:
        return np.random
    if isinstance(seed, int):
        return np.random.RandomState(seed)
    return seed


def gen_annual_income(
    number_control_per_week: Union[int, List[int]],
    effect_size: float,
    inc_base_rate: int = 36_121,
    inc_base_std: int = 5_000,
    inc_treatment_std: int = 5_000,
    number_of_weeks: int = 13,
    number_treat_per_week: int = 150,
    seed: Optional[Union[int, np.random.mtrand.RandomState]] = 189389,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generates annual income before and after RESEA intervention according to a normal
    distribution using `np.random.randn`. The initial_value is used in generating
    outcome_value to ensure some correlation.

    Args:
        number_control_per_week: a single number if control does not vary weekly.
            List of int otherwise
        effect_size: used to define the treatment effect, which modifies the mean of
            generated data
        inc_base_rate: average income per capita in RI in 2019 according to
            https://www.census.gov/quickfacts/fact/table/RI,US/INC110219
        inc_base_std: standard deviation for the normal distribution generation
        inc_treatment_std: given the randomness of assignemnt to treatment, there
            should be no difference between base and treatment a priori
        number_of_weeks: how many cohorts we want to generate. Defaults to 13 because
            we generate data quarterly
        number_treat_per_week: number of individuals selected for treatment.
            Defaults to 150 based on DLT's experiment design
        seed: seed for randomization

    Returns: treated_df, control_df
    """
    random = _convert_seed_to_randomstate(seed)

    # Define the effect
    inc_treatment_effect = inc_base_rate * effect_size

    inc_initial_value_of_treated = (
        random.randn(number_of_weeks * number_treat_per_week) * inc_base_std
        + inc_base_rate
    )
    inc_outcome_value_of_treated = (
        inc_initial_value_of_treated
        + random.randn(number_of_weeks * number_treat_per_week) * inc_treatment_std
        + inc_treatment_effect
    )

    inc_initial_value_of_control = (
        random.randn(number_of_weeks * number_control_per_week) * inc_base_std
        + inc_base_rate
    )

    inc_outcome_value_of_control = (
        random.randn(number_of_weeks * number_control_per_week) * inc_base_std
        + inc_base_rate
    )
    control_df = pd.DataFrame(
        {
            "inc_initial": inc_initial_value_of_control,
            "inc_outcome": inc_outcome_value_of_control,
        }
    )
    treated_df = pd.DataFrame(
        {
            "inc_initial": inc_initial_value_of_treated,
            "inc_outcome": inc_outcome_value_of_treated,
        }
    )
    return treated_df, control_df


def gen_employment(
    number_control_per_week: Union[int, List[int]],
    effect_size: float,
    emp_base_rate: float = 0.62,
    number_of_weeks: int = 13,
    number_treat_per_week=150,
    seed: Optional[Union[int, np.random.mtrand.RandomState]] = 189389,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generates employment outcomes after RESEA intervention according to a binomial
    distribution using `np.random.binomial`. Input for binomial distribution is
    determined by `effect_size` and `emp_base_rate` variables.

    Args:
        number_control_per_week: a single number if control does not vary weekly.
            List of int otherwise
        effect_size: used to define the treatment effect, which modifies the mean of
            generated data
        emp_base_rate: default reemployment rate assuming no RESEA interventionn.
            Defaults to 0.62, which was the reemployment rate at Boston for 2018
            according to https://oui.doleta.gov/unemploy/uir_rates.asp
        number_of_weeks: how many cohorts we want to generate. Defaults to 13 because
            we generate data quarterly
        number_treat_per_week: number of individuals selected for treatment.
            Defaults to 150 based on DLT's experiment design
        seed: seed for randomization

    Returns: treated_df, control_df
    """
    random = _convert_seed_to_randomstate(seed)

    # the amount we expect incrased
    emp_treatment_effect = float(emp_base_rate * (1 + effect_size))

    try:
        emp_outcome_value_of_treated = random.binomial(
            1, emp_treatment_effect, size=number_of_weeks * number_treat_per_week
        )
    except ValueError:
        print(f"error at {emp_treatment_effect}")
    try:
        emp_outcome_value_of_control = random.binomial(
            1,
            emp_base_rate,
            size=number_of_weeks * number_control_per_week,
        )
    except ValueError:
        print(f"error at {emp_base_rate}")

    treated_df = pd.DataFrame({"employment": emp_outcome_value_of_treated})
    control_df = pd.DataFrame({"employment": emp_outcome_value_of_control})
    return treated_df, control_df


def gen_pay_ratio(
    number_control_per_week: Union[int, List[int]],
    effect_size: float,
    pay_ratio_lambda=0.5,
    pay_ratio_min=11.50,
    distribution: str = "exponential",
    number_of_weeks: int = 13,
    number_treat_per_week=150,
    seed: Optional[Union[int, np.random.mtrand.RandomState]] = 189389,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generates pay ratio outcomes after RESEA intervention according to a distribution.
    The distribution can be exponential or pareto depending on the user's assumptions
    about the population of individuals eligible for unemployment. Specifically, the
    exponential distribution assumes the majority of individuals are making close to
    minimum wage, while the pareto assumes a heavier tail.

    As everyone is assumed from an initial pay ratio of 0; we only generate the outcome
    ratio.

    Args:
        number_control_per_week: a single number if control does not vary weekly. List of int otherwise
        effect_size: used to define the treatment effect, which modifies the mean of generated data
        pay_ratio_lambda: input for exponential and pareto distribution.
        pay_ratio_min: minimum wage for RI in 2021
        distribution: selection of data generating distribution; either exponential or pareto
        number_of_weeks: how many cohorts we want to generate. Defaults to 13 because we generate data quarterly.
        number_treat_per_week: number of individuals selected for treatment.
            Defaults to 150 based on DLT's experiment design
        seed: seed for randomization

    Returns: treated_df, control_df
    """
    random = _convert_seed_to_randomstate(seed)

    if distribution == "exponential":
        pay_ratio_outcome_value_of_treated = (
            random.exponential(
                pay_ratio_lambda, number_of_weeks * number_treat_per_week
            )
            * (1 - effect_size)
            + 1
        ) * pay_ratio_min
        pay_ratio_outcome_value_of_control = (
            random.exponential(
                pay_ratio_lambda,
                number_of_weeks * number_control_per_week,
            )
            + 1
        ) * pay_ratio_min

    elif distribution == "pareto":
        pay_ratio_outcome_value_of_treated = (
            random.pareto(1 / pay_ratio_lambda, number_of_weeks * number_treat_per_week)
            + 1 * (1 - effect_size)
        ) * pay_ratio_min
        pay_ratio_outcome_value_of_control = (
            random.pareto(
                1 / pay_ratio_lambda,
                number_of_weeks * number_control_per_week,
            )
            + 1
        ) * pay_ratio_min
    else:
        raise ValueError(
            f"distribution must be one of 'pareto' or 'exponential', not {distribution}"
        )

    treated_df = pd.DataFrame({"pay_ratio": pay_ratio_outcome_value_of_treated})
    control_df = pd.DataFrame({"pay_ratio": pay_ratio_outcome_value_of_control})
    return treated_df, control_df


def gen_weeks_on_unemployment(
    number_control_per_week: Union[int, List[int]],
    effect_size: float,
    qt_unemp_lambda: float = 3,
    number_of_quarters: int = 6,
    number_of_weeks: int = 13,
    number_treat_per_week: int = 150,
    seed: Optional[Union[int, np.random.mtrand.RandomState]] = 189389,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generates weeks of unemployment after RESEA intervention according to a exponential
    distribution using `np.random.exponential`. Input for exponential distribution is
    determined by `qt_unemp_lambda` and `number_of_quarters` variables.

    Args:
        number_control_per_week: a single number if control does not vary weekly. List of int otherwise
        effect_size: used to define the treatment effect, which modifies the mean of generated data
        qt_unemp_lambda: expected frequency of weeks on unemployment for quarter.
            source: https://www.bls.gov/web/empsit/cpseea12.htm
        number_of_quarters: The number of quarters. Defaults to 6 to adjust the lambda rate for the 1.5 year study period.
        number_of_weeks: how many cohorts we want to generate. Defaults to 13 because we generate data quarterly.
        number_treat_per_week: number of individuals selected for treatment.
            Defaults to 150 based on DLT's experiment design
        seed: seed for randomization

    Returns: treated_df, control_df

    """
    random = _convert_seed_to_randomstate(seed)

    # attempt to estimate this as exponential distribution,
    # because the event can be modeled as the time between occurrances
    unemp_lambda = qt_unemp_lambda * number_of_quarters
    unemp_treatment_effect = unemp_lambda * (1 - effect_size)
    unemp_outcome_value_of_treat = random.exponential(
        unemp_treatment_effect, size=number_of_weeks * number_treat_per_week
    )
    unemp_outcome_value_of_control = random.exponential(
        unemp_lambda, size=number_of_weeks * number_control_per_week
    )
    treated_df = pd.DataFrame({"wks_unemp": unemp_outcome_value_of_treat})
    control_df = pd.DataFrame({"wks_unemp": unemp_outcome_value_of_control})
    return treated_df, control_df


def gen_cohorts(
    df: pd.DataFrame,
    cohort_unit: int,
    is_treated: bool = True,
) -> pd.DataFrame:
    """
    N.B. alters df in place and also returns it
    """
    if is_treated:
        df["cohort"] = np.arange(len(df), dtype=int) // cohort_unit
        df["is_treated"] = True
    else:
        df["cohort"] = np.arange(len(df), dtype=int) // cohort_unit
        df["is_treated"] = False
    ### Alternatively, this is where we implement the reduction if we want weekly variation
    return df
