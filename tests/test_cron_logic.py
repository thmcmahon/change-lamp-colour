#!/usr/bin/env python3
"""
Unit tests for cron‐string logic in GitHub Actions workflow.
"""
import unittest
from typing import Optional


def get_scheduled_color(cron: str) -> Optional[str]:
    """
    Determine which color to set based on the cron schedule string.
    Only the following exact minute/hour pairs are valid:
      - minute '45', hour '19' or '20' => green
      - minute '0',  hour '23' or '0'  => yellow
    """
    parts = cron.split()
    if len(parts) < 2:
        return None
    minute, hour = parts[0], parts[1]
    # Green at 6:45 local (UTC+11=19, UTC+10=20)
    if minute == '45' and hour in ('19', '20'):
        return 'green'
    # Yellow at 10:00 local (UTC+11=23, UTC+10=0)
    if minute == '0' and hour in ('23', '0'):
        return 'yellow'
    return None


class TestCronLogic(unittest.TestCase):
    def test_green_triggers(self):
        # Both UTC+11 (19) and UTC+10 (20) should map to green at 6:45
        for hour in ('19', '20'):
            cron = f'45 {hour} * * *'
            self.assertEqual(
                get_scheduled_color(cron),
                'green',
                f"Expected green for cron '{cron}'"
            )

    def test_yellow_triggers(self):
        # Both UTC+11 (23) and UTC+10 (0) should map to yellow at 10:00
        for hour in ('23', '0'):
            cron = f'0 {hour} * * *'
            self.assertEqual(
                get_scheduled_color(cron),
                'yellow',
                f"Expected yellow for cron '{cron}'"
            )

    def test_non_matching(self):
        # Any other schedule should not map to a color
        non_crons = ['30 12 * * *', '15 8 * * *', 'random entry']
        for cron in non_crons:
            self.assertIsNone(
                get_scheduled_color(cron),
                f"Expected None for non-matching cron '{cron}'"
            )
    
    def test_wrong_dst_hours(self):
        # Ensure times adjacent to DST/non-DST hours do not fire
        wrong_times = [
            ('45', '18'),  # one hour before AEDT green
            ('45', '21'),  # one hour after AEST green
            ('0', '22'),   # one hour before AEDT yellow
            ('0', '1')     # one hour after AEST yellow
        ]
        for minute, hour in wrong_times:
            cron = f"{minute} {hour} * * *"
            with self.subTest(cron=cron):
                self.assertIsNone(
                    get_scheduled_color(cron),
                    f"Expected None for wrong DST hour cron '{cron}'"
                )


if __name__ == '__main__':
    unittest.main()