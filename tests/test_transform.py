import unittest
import pandas as pd
from transform import transform_master_data, transform_transactional_data


class TestTransform(unittest.TestCase):

    def test_transform_master_data(self):
        # Sample input DataFrame
        df = pd.DataFrame({
            'EmployeeID': [1, 2, 3],
            'LastName': ['Smith', 'Jones', None],
            'FirstName': ['John', 'Jane', 'Joe']
        })
        required_columns = ['EmployeeID', 'LastName', 'FirstName']

        # Transform the data
        transformed_df = transform_master_data(df, required_columns)

        # Expected output DataFrame
        expected_df = pd.DataFrame({
            'EmployeeID': [1, 2, 3],
            'LastName': ['Smith', 'Jones', 'UNKNOWN'],
            'FirstName': ['John', 'Jane', 'Joe']
        })

        # Assertions
        pd.testing.assert_frame_equal(transformed_df, expected_df)

    def test_transform_transactional_data(self):
        # Implement similar to transform_master_data
        pass


if __name__ == '__main__':
    unittest.main()
