import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from helpers.s3_utils import extract_from_s3


class TestExtract(unittest.TestCase):

    @patch('helpers.s3_utils.extract_from_s3')
    def test_extract_success(self, mock_extract_from_s3):
        # Set up mock
        mock_df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        mock_extract_from_s3.return_value = mock_df

        # Call the function
        result = extract_from_s3(
            'mock-client', 'mock-bucket', 'mock-prefix', 'mock-file.csv'
        )

        # Assertions
        pd.testing.assert_frame_equal(result, mock_df)

    @patch('helpers.s3_utils.extract_from_s3')
    def test_extract_failure(self, mock_extract_from_s3):
        # Set up mock to raise an exception
        mock_extract_from_s3.side_effect = Exception("S3 access error")

        # Call the function and check for exception
        with self.assertRaises(Exception) as context:
            extract_from_s3(
                'mock-client', 'mock-bucket', 'mock-prefix', 'mock-file.csv'
            )
        self.assertEqual(str(context.exception), "S3 access error")


if __name__ == '__main__':
    unittest.main()
