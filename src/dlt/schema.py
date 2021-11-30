""" Define the Schemas used for checking raw datasets from DLT"""
import pandera.extensions as extensions
from pandera import Check, Column, DataFrameSchema


@extensions.register_check_method(
    statistics=["val"],
    check_type="element_wise",
)
def date_length(element, *, val):
    """
    Element-wise check of value lengths
    """
    return len(element) == val


@extensions.register_check_method(
    statistics=["val"],
    check_type="element_wise",
)
def ssn_length(element, *, min_value, max_value):
    """
    Element-wise check of values between min_value and max_value
    """
    return (min_value <= element) & (element <= max_value)


# Establish a schema of the most commonly shared cells.
# The checks focus on ensuring that the columns that are used for merging have the correct types and lengths
raw_data_schema = DataFrameSchema(
    {
        "EFFECTIVE_DATE": Column(
            str,
            coerce=True,
            required=False,
            checks=Check.date_length(8),
        ),
        "LOCAL_OFFICE_NO": Column(int, coerce=True, required=False),
        "SSN": Column(
            int,
            coerce=True,
            checks=Check.ssn_length(min_value=1_01_0001, max_value=999_99_9999),
        ),
        "NAME_FIRST": Column(str, coerce=True, required=False),
        "NAME_MIDDLE": Column(str, coerce=True, required=False, nullable=True),
        "NAME_LAST": Column(str, coerce=True, required=False),
        "SENT_DATE": Column(
            str,
            coerce=True,
            required=False,
            checks=Check.date_length(8),
        ),
        "USERID": Column(str, coerce=True, required=False),
        "FIRST_PAY_DATE": Column(
            str,
            coerce=True,
            required=False,
            checks=Check.date_length(8),
        ),
    },
    strict="filter",
)
