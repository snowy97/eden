# -*- coding: utf-8 -*-

ClimateDataPortal = local_import("ClimateDataPortal")
Climate_DSL = local_import("ClimateDataPortal.DSL")
Units = Climate_DSL.Units

# tests ---------------------------------------

# place/month
# missing data for a key shouldn't cause misalignments - need to merge

def compare(actual_units, expected_units):
    assert actual_units == expected_units, actual_units

def compare_parsed_units(unit_string, expected_units):
    compare(Units.parsed_from(unit_string), expected_units)

def test_unit_parsing_mm():
    compare_parsed_units("mm", Units({"mm":1}, True))

def test_unit_parsing_mps():
    compare_parsed_units("m/s", Units({"m":1, "s":-1}, True))

def test_unit_parsing_hertz():
    compare_parsed_units("/s", Units({"s":-1}, True))

def test_unit_parsing_complex():
    compare_parsed_units("m^2kg/s^2", Units({"s":-2, "kg":1, "m":2}, True))

def test_unit_parsing_complex_with_spaces():
    compare_parsed_units(" kg m^2 / s^2 ", Units({"s":-2, "kg":1, "m":2}, True))

def test_unit_addition():
    compare(
        Units({"s":-2, "kg":1, "m":2}, True) + Units({"s":-2, "kg":1, "m":2}, True),
        Units({"s":-2, "kg":1, "m":2}, True)
    )

def test_unit_subtraction():
    compare(
        Units({"s":-2, "kg":1, "m":2}, True) - Units({"s":-2, "kg":1, "m":2}, True),
        Units({"s":-2, "kg":1, "m":2}, False)
    )

def test_unit_subtract_delta():
    compare(
        Units({"s":-2, "kg":1, "m":2}, True) - Units({"s":-2, "kg":1, "m":2}, False),
        Units({"s":-2, "kg":1, "m":2}, True)
    )

def test_unit_multiplication():
    compare(
        Units({"m":2}, True) * Units({"s":-2, "kg":1}, True),
        Units({"s":-2, "kg":1, "m":2}, True)
    )
    
def test_unit_division():
    compare(
        Units({"s":-2, "kg":1, "m":2}, True) / Units({"s":-2, "kg":1}, True),
        Units({"m":2}, True) 
    )

def test_unit_division_to_dimensionless():
    compare(
        Units({"s":-2, "kg":1, "m":2}, True) / Units({"s":-2, "kg":1, "m":2}, True),
        Units({}, True) 
    )

def test_unit_squaring():
    compare(
        Units({"s":-2, "kg":1}, True) ** 2,
        Units({"s":-4, "kg":2}, True)
    )

def test_unit_square_root():
    compare(
        Units({"s":-4, "kg":2}, True) ** (1/2.0),
        Units({"s":-2, "kg":1}, True)
    )

def test_parse_affine_units():
    compare(
        Units.parsed_from("kg")._positive, True
    )

def test_parse_vector_units():
    compare(
        Units.parsed_from("delta kg")._positive, False
    )
    compare(
        Units.parsed_from("Δ kg")._positive, False
    )

def test_subtracting_an_affine_number_from_an_affine_value():
    compare(
        Units.parsed_from("kg") - Units.parsed_from("kg"),
        Units.parsed_from("delta kg")
    )

def test_subtracting_a_delta_from_an_affine_value():
    compare(
        Units.parsed_from("kg") - Units.parsed_from("delta kg"),
        Units.parsed_from("kg")
    )

def test_adding_a_delta_to_an_affine_value():
    compare(
        Units.parsed_from("kg") + Units.parsed_from("delta kg"),
        Units.parsed_from("kg")
    )

def test_adding_an_affine_value_to_a_delta():
    compare(
        Units.parsed_from("delta kg") + Units.parsed_from("kg"),
        Units.parsed_from("kg")
    )

def test_adding_two_affine_values():
    # actually this is kind of nonsense, but it needs to work
    compare(
        Units.parsed_from("kg") + Units.parsed_from("kg"),
        Units.parsed_from("kg")
    )

def test_adding_two_delta_values():
    compare(
        Units.parsed_from("delta kg") + Units.parsed_from("delta kg"),
        Units.parsed_from("delta kg")
    )

def test_subtracting_two_delta_values():
    compare(
        Units.parsed_from("delta kg") - Units.parsed_from("delta kg"),
        Units.parsed_from("delta kg")
    )

def compare_analysis(expression_string, expected_analysis):
    try:
        Climate_DSL.parse(expression_string)
    except TypeError, error:
        assert str(error) == expected_analysis
    else:
        assert False, "TypeError wasn't raised"

def test_analysis():
    compare_analysis(
        """Average("Observed Rainfall", FromDate(1960, 1, 1), ToDate(1, 1,1)) - 2""",
        """(
    Average(
        "Observed Rainfall",
        FromDate(1960, 1, 1)
        ToDate(1, 1, 1)
        # ^ Year should be in range 1900 to 2500
    )
    -
    2.0
)"""
    )

def compare_expression_units(expression_string, expected_units):
    expression = Climate_DSL.parse(expression_string)
    actual_units = Climate_DSL.units(expression)
    assert actual_units == expected_units, actual_units

def test_parsing_expressions_1():
    compare_expression_units(
        """Average("Observed Rainfall", FromDate(1960, 1, 1), ToDate(1961, 1,1)) - 2 mm""", 
        Units.parsed_from("delta mm")
    )

def test_parsing_expressions_1b():
    compare_expression_units(
        """Average("Observed Rainfall", FromDate(1960, 1, 1), ToDate(1961, 1,1)) - 2 delta mm""", 
        Units.parsed_from("mm")
    )

def test_parsing_expressions_2():
    compare_expression_units(
    """Average("Observed Rainfall", FromDate(1960, 1, 1), ToDate(1961, 1,1)) ** 2""",
        Units.parsed_from("mm^2"))
    
def test_parsing_expressions_3():
    compare_expression_units(
    """
            Average(
                "Gridded Rainfall",
                FromDate(1980, 1, 1),
                ToDate(2000, 12, 31),
                Months(Jul, Aug, Sep, Oct, Nov, December, Jan, Feb, Mar, April)
            )
            / 
            Average(
                "Gridded Rainfall",
                FromDate(1990, 1, 1),
                ToDate(2010, 12, 31)
            )
        """, Units.parsed_from("")
    )

def test_parsing_expressions_4():
    compare_expression_units(
        """
            Average(
                "Gridded Rainfall",
                FromDate(1980, 1, 1),
                ToDate(2000, 12, 31),
                Months(Jul, Aug, Sep, Oct, Nov, December, Jan, Feb, Mar, April)
            )
            - 
            Average(
                "Gridded Rainfall",
                FromDate(1990, 1, 1),
                ToDate(2010, 12, 31)
            )
        """, Units.parsed_from("delta mm")
    )

def test_parsing_expressions_5():
    compare_expression_units(
        """
        Maximum(
            "Observed Max Temp",
            FromDate(1950, Jan),
            ToDate(2011, Jul)
        )
        """, Units.parsed_from("Kelvin")
    )
        
def test_compare_months_for_two_different_years():
    raise NotImplementedError
    


failures = 0
for name, function in dict(globals()).iteritems():
    if name.startswith("test"):
        print name
        try:
            function()
        except Exception, exception:
            print type(exception).__name__, exception
            failures += 1
        else:
            print "OK"
print failures, "Failures"