import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from load import load_master_data, load_transactional_data

class TestLoad(unittest.TestCase):

    @patch('load.stage_data')
    def test_load_master_data(self, mock_stage_data):
        df = pd.DataFrame({
            'EmployeeID': [1, 2, 3],
            'LastName': ['Smith', 'Jones', 'Doe']
        })
        engine = MagicMock()
        table_name = 'DimEmployee'

        # Call the function
        load_master_data(df, table_name, engine)

        # Assertions
        mock_stage_data.assert_called_once_with(df, table_name)

    @patch('load.create_fact_table')
    @patch('load.stage_data')
    def test_load_transactional_data(self, mock_stage_data, mock_create_fact_table):
        df = pd.DataFrame({
            'EmployeeID': [1, 2, 3],
            'BaseSalary': [50000, 60000, 70000]
        })
        engine = MagicMock()

        # Call the function
        load_transactional_data(df, engine)

        # Assertions
        mock_create_fact_table.assert_called_once()
        mock_stage_data.assert_called_once_with(df, 'FactPayroll')

if __name__ == '__main__':
    unittest.main()
