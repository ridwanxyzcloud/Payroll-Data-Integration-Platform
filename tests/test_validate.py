import unittest
import pandas as pd
from validate import validate_and_clean_data


class TestValidate(unittest.TestCase):

    def test_validate_and_clean_data(self):
        # Sample DataFrame with missing and invalid data
        df = pd.DataFrame({
            'col1': [1, 2, None, -5, 1000],
            'col2': ['a', 'b', None, 'd', 'e']
        })
        dim_columns = ['col1', 'col2']

        # Validate and clean data
        cleaned_df = validate_and_clean_data(df, dim_columns)

        # Expected output DataFrame
        expected_df = pd.DataFrame({
            'col1': [1, 2, 1, 1, 1],
            'col2': ['a', 'b', 'UNKNOWN', 'd', 'e']
        })

        # Assertions
        pd.testing.assert_frame_equal(cleaned_df, expected_df)


if __name__ == '__main__':
    unittest.main()
