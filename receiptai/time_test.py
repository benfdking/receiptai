import unittest
from datetime import date
from unittest.mock import patch

from time_mcp import (
    get_today, get_tomorrow, get_next_week, get_last_week,
    get_next_month, get_last_month, get_next_year, get_last_year,
    get_specific_range, get_relative_date, get_past_relative_date
)


class TestDateFunctions(unittest.TestCase):
    """Test cases for the date functions in time_mcp.py"""

    @patch('time_mcp.date')
    def test_get_today(self, mock_date):
        """Test get_today returns today's date in ISO format."""
        # Set up mock return value for date.today()
        mock_today = date(2023, 5, 15)
        mock_date.today.return_value = mock_today

        result = get_today()
        self.assertEqual(result, "2023-05-15")
        mock_date.today.assert_called_once()

    @patch('time_mcp.date')
    def test_get_tomorrow(self, mock_date):
        """Test get_tomorrow returns tomorrow's date in ISO format."""
        mock_today = date(2023, 5, 15)
        mock_date.today.return_value = mock_today

        # Need to allow timedelta to work normally
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        result = get_tomorrow()
        self.assertEqual(result, "2023-05-16")

    @patch('time_mcp.date')
    def test_get_next_week(self, mock_date):
        """Test get_next_week returns correct start and end dates of next week."""
        # Monday
        mock_today = date(2023, 5, 15)
        mock_date.today.return_value = mock_today

        # Allow normal date behavior for calculations
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        result = get_next_week()
        self.assertEqual(result, {'start': '2023-05-22', 'end': '2023-05-28'})

        # Test with a different day of week (Wednesday)
        mock_today = date(2023, 5, 17)
        mock_date.today.return_value = mock_today

        result = get_next_week()
        self.assertEqual(result, {'start': '2023-05-22', 'end': '2023-05-28'})

    @patch('time_mcp.date')
    def test_get_last_week(self, mock_date):
        """Test get_last_week returns correct start and end dates of last week."""
        # Monday
        mock_today = date(2023, 5, 15)
        mock_date.today.return_value = mock_today

        # Allow normal date behavior for calculations
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        result = get_last_week()
        # Last week would be May 8-14 when today is May 15 (a Monday)
        self.assertEqual(result, {'start': '2023-05-08', 'end': '2023-05-14'})

    @patch('time_mcp.date')
    def test_get_next_month(self, mock_date):
        """Test get_next_month returns correct start and end dates of next month."""
        # May
        mock_today = date(2023, 5, 15)
        mock_date.today.return_value = mock_today

        # Allow normal date behavior for calculations
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        result = get_next_month()
        self.assertEqual(result, {'start': '2023-06-01', 'end': '2023-06-30'})

        # Test December to January transition (year change)
        mock_today = date(2023, 12, 15)
        mock_date.today.return_value = mock_today

        result = get_next_month()
        self.assertEqual(result, {'start': '2024-01-01', 'end': '2024-01-31'})

    @patch('time_mcp.date')
    def test_get_last_month(self, mock_date):
        """Test get_last_month returns correct start and end dates of last month."""
        # May
        mock_today = date(2023, 5, 15)
        mock_date.today.return_value = mock_today

        # Allow normal date behavior for calculations
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        result = get_last_month()
        self.assertEqual(result, {'start': '2023-04-01', 'end': '2023-04-30'})

        # Test January to December transition (year change)
        mock_today = date(2023, 1, 15)
        mock_date.today.return_value = mock_today

        result = get_last_month()
        self.assertEqual(result, {'start': '2022-12-01', 'end': '2022-12-31'})

    @patch('time_mcp.date')
    def test_get_next_year(self, mock_date):
        """Test get_next_year returns correct start and end dates of next year."""
        mock_today = date(2023, 5, 15)
        mock_date.today.return_value = mock_today

        # Allow normal date behavior for calculations
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        result = get_next_year()
        self.assertEqual(result, {'start': '2024-01-01', 'end': '2024-12-31'})

    @patch('time_mcp.date')
    def test_get_last_year(self, mock_date):
        """Test get_last_year returns correct start and end dates of last year."""
        mock_today = date(2023, 5, 15)
        mock_date.today.return_value = mock_today

        # Allow normal date behavior for calculations
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        result = get_last_year()
        self.assertEqual(result, {'start': '2022-01-01', 'end': '2022-12-31'})

    def test_get_specific_range(self):
        """Test get_specific_range returns correct range with given start and end dates."""
        result = get_specific_range('2023-05-01', '2023-05-31')
        self.assertEqual(result, {'start': '2023-05-01', 'end': '2023-05-31'})

        # Test with invalid date
        with self.assertRaises(ValueError):
            get_specific_range('2023-05-32', '2023-06-01')

    @patch('time_mcp.date')
    def test_get_relative_date(self, mock_date):
        """Test get_relative_date returns correct future date."""
        mock_today = date(2023, 5, 15)
        mock_date.today.return_value = mock_today
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        # Test days
        self.assertEqual(get_relative_date(5, 'days'), '2023-05-20')

        # Test weeks
        self.assertEqual(get_relative_date(2, 'weeks'), '2023-05-29')

        # Test months
        self.assertEqual(get_relative_date(3, 'months'), '2023-08-15')

        # Test month with day overflow (31 -> 30)
        mock_today = date(2023, 1, 31)
        mock_date.today.return_value = mock_today
        self.assertEqual(get_relative_date(1, 'months'), '2023-02-28')

        # Test with leap year
        mock_today = date(2024, 1, 31)
        mock_date.today.return_value = mock_today
        self.assertEqual(get_relative_date(1, 'months'), '2024-02-29')

        # Test invalid unit
        self.assertIsNone(get_relative_date(1, 'invalid_unit'))  # type: ignore

    @patch('time_mcp.date')
    def test_get_past_relative_date(self, mock_date):
        """Test get_past_relative_date returns correct past date."""
        mock_today = date(2023, 5, 15)
        mock_date.today.return_value = mock_today
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        # Test days
        self.assertEqual(get_past_relative_date(5, 'days'), '2023-05-10')

        # Test weeks
        self.assertEqual(get_past_relative_date(2, 'weeks'), '2023-05-01')

        # Test months
        self.assertEqual(get_past_relative_date(3, 'months'), '2023-02-15')

        # Test month with day overflow (31 -> 28/29)
        mock_today = date(2023, 3, 31)
        mock_date.today.return_value = mock_today
        self.assertEqual(get_past_relative_date(1, 'months'), '2023-02-28')

        # Test with leap year
        mock_today = date(2024, 3, 31)
        mock_date.today.return_value = mock_today
        self.assertEqual(get_past_relative_date(1, 'months'), '2024-02-29')

        # Test invalid unit
        self.assertIsNone(get_past_relative_date(1, 'invalid_unit'))  # type: ignore

    @patch('time_mcp.date')
    def test_month_transitions(self, mock_date):
        """Test edge cases with month transitions."""
        # Testing transitions across multiple months
        mock_today = date(2023, 5, 15)
        mock_date.today.return_value = mock_today
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        self.assertEqual(get_relative_date(18, 'months'), '2024-11-15')
        self.assertEqual(get_past_relative_date(18, 'months'), '2021-11-15')


if __name__ == '__main__':
    unittest.main()
