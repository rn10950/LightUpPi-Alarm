#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Unit test for the AlarmItem class.
#
# Copyright (c) 2015 carlosperate https://github.com/carlosperate/
# Licensed under The MIT License (MIT), a copy can be found in the LICENSE file
#
from __future__ import unicode_literals, absolute_import
import unittest
import mock
import io
try:
    from LightUpAlarm.AlarmItem import AlarmItem
except ImportError:
    import os
    import sys
    file_dir = os.path.dirname(os.path.realpath(__file__))
    package_dir = os.path.dirname(os.path.dirname(file_dir))
    sys.path.insert(0, package_dir)
    from LightUpAlarm.AlarmItem import AlarmItem


class AlarmItemTestCase(unittest.TestCase):
    """ Tests for AlarmItem class. """

    #
    # Helper methods
    #
    def assert_repeat(self, alarm_test, days):
        self.assertEqual(alarm_test.monday, days[0])
        self.assertEqual(alarm_test.tuesday, days[1])
        self.assertEqual(alarm_test.wednesday, days[2])
        self.assertEqual(alarm_test.thursday, days[3])
        self.assertEqual(alarm_test.friday, days[4])
        self.assertEqual(alarm_test.saturday, days[5])
        self.assertEqual(alarm_test.sunday, days[6])

    def assert_stderr(self, test_srderr, equal=False):
        """ Checks the stderr error string and resets it for next test. """
        if equal is True:
            self.assertEqual(test_srderr.getvalue(), '')
        else:
            self.assertNotEqual(test_srderr.getvalue(), '')
        test_srderr.truncate(0)
        test_srderr.write('')
        self.assertEqual(test_srderr.getvalue(), '')

    #
    # Tests
    #
    def test_constructor(self):
        """ Tests valid inputs to the constructor. """
        id_ = 265
        hour = 23
        minute = 59
        days = (False, True, True, False, False, False, False)
        label = 'Alarm label'
        timestamp = 12345678

        # Check constructor with minimum arguments
        alarm_test = AlarmItem(hour, minute)
        self.assertEqual(hour, alarm_test.hour)
        self.assertEqual(minute, alarm_test.minute)
        for day in alarm_test.repeat:
            self.assertEqual(alarm_test.repeat[day], False)
        self.assertEqual(alarm_test.label, '')
        self.assertIsNone(alarm_test.timestamp)

        # Check constructor with minimum arguments + repeat days
        alarm_test = AlarmItem(hour, minute, days=days)
        self.assertEqual(days, alarm_test.repeat)

        # Check constructor with minimum arguments + repeat days + enabled
        alarm_test = AlarmItem(hour, minute, days=days, enabled=False)
        self.assertEqual(False, alarm_test.enabled)

        # Check constructor with minimum arguments + repeat days + enabled +
        # label
        alarm_test = AlarmItem(
            hour, minute, days=days, enabled=False, label=label)
        self.assertEqual(label, alarm_test.label)

        # Check constructor with minimum arguments + repeat days + enabled +
        # label + timestamp
        alarm_test = AlarmItem(hour, minute, days=days, enabled=False,
                               label=label, timestamp=timestamp)
        self.assertEqual(timestamp, alarm_test.timestamp)

        # Check constructor with minimum arguments + repeat days + enabled +
        # label + id
        alarm_test = AlarmItem(hour, minute, days=days, enabled=False,
                               label=label, timestamp=timestamp, alarm_id=id_)
        self.assertEqual(id_, alarm_test.id_)

    def test_constructor_hour_min_range(self):
        """
        Test constructor values for hours and minutes to produce a None object
        if they are larger than 23 and 59 respectively.
        """
        # The accessor functions print to stderr if bad data is encountered, so
        # we need to capture stderr to test it.
        with mock.patch('sys.stderr', new=io.StringIO()) as test_srderr:
            # Invalid minute
            self.assertEqual(test_srderr.getvalue(), '')
            alarm_test = AlarmItem(23, 60)
            self.assertIsNone(alarm_test)
            self.assert_stderr(test_srderr)
            alarm_test = AlarmItem(23, -50)
            self.assertIsNone(alarm_test)
            self.assert_stderr(test_srderr)

            # Invalid hour
            alarm_test = AlarmItem(24, 59)
            self.assertIsNone(alarm_test)
            self.assert_stderr(test_srderr)
            alarm_test = AlarmItem(-12, 59)
            self.assertIsNone(alarm_test)
            self.assert_stderr(test_srderr)

            # Invalid hour and minute
            alarm_test = AlarmItem(24, 60)
            self.assertIsNone(alarm_test)
            self.assert_stderr(test_srderr)
            alarm_test = AlarmItem(-16, -45)
            self.assertIsNone(alarm_test)
            self.assert_stderr(test_srderr)

    def test_hour_min_loop_range(self):
        """
        Test setting the hours and minutes accessors to not change values with
        invalid inputs.
        """
        alarm_test = AlarmItem(0, 1)
        # The accessor functions print to stderr if bad data is encountered, so
        # we need to capture stderr to test it.
        with mock.patch('sys.stderr', new=io.StringIO()) as test_srderr:
            self.assertEqual(test_srderr.getvalue(), '')
            alarm_test.hour = 12
            alarm_test.minute = 34
            self.assertEqual(alarm_test.hour, 12)
            self.assertEqual(alarm_test.minute, 34)
            self.assert_stderr(test_srderr, equal=True)

            # Invalid ints
            alarm_test.minute = 60
            self.assert_stderr(test_srderr)
            alarm_test.minute = -1
            self.assert_stderr(test_srderr)
            self.assertEqual(alarm_test.minute, 34)

            alarm_test.hour = 24
            self.assert_stderr(test_srderr)
            alarm_test.hour = -2
            self.assert_stderr(test_srderr)
            self.assertEqual(alarm_test.hour, 12)

            self.assertEqual(alarm_test.hour, 12)
            self.assertEqual(alarm_test.minute, 34)

    def test_hour_min_integers(self):
        """
        Test setting the hours and minutes values valid integers and non-integer
        values.
        """
        alarm_test = AlarmItem(0, 0)

        # The accessor functions print to stderr if bad data is encountered, so
        # we need to capture stderr to test it.
        with mock.patch('sys.stderr', new=io.StringIO()) as test_srderr:
            # First ensure that successful set does not write to stderr
            self.assertEqual(test_srderr.getvalue(), '')
            alarm_test.hour = 12
            alarm_test.minute = 34
            self.assert_stderr(test_srderr, equal=True)

            # Float instead of integer
            alarm_test.hour = 12.34
            self.assert_stderr(test_srderr)
            alarm_test.minute = 34.56
            self.assert_stderr(test_srderr)

            # String instead of integer
            alarm_test.hour = 'minutes'
            self.assert_stderr(test_srderr)
            alarm_test.minute = 'hours'
            self.assert_stderr(test_srderr)

            self.assertEqual(alarm_test.hour, 12)
            self.assertEqual(alarm_test.minute, 34)

    def test_repeat_list_strictness(self):
        """
        Test that the repeat list of booleans is filtered and catches invalid
        inputs. Including lists of not booleans, and boolean lists with and
        incorrect number of items.
        """
        alarm_test = AlarmItem(0, 0)
        valid_days = (False, True, True, False, False, False, False)

        # Setting a valid value
        self.assertNotEqual(valid_days, alarm_test.repeat)
        alarm_test.repeat = valid_days
        self.assertEqual(valid_days, alarm_test.repeat)

        # The accessor functions print to stderr if bad data is encountered, so
        # we need to capture stderr to test it.
        with mock.patch('sys.stderr', new=io.StringIO()) as test_srderr:
            # First ensure that successful set does not write to stderr
            self.assertEqual(test_srderr.getvalue(), '')
            alarm_test.repeat = valid_days
            self.assertEqual(alarm_test.repeat, valid_days)
            self.assertEqual(test_srderr.getvalue(), '')

            # Too many arguments
            alarm_test.repeat = (
                False, False, False, False, False, False, False, False)
            self.assert_stderr(test_srderr)
            self.assertEqual(alarm_test.repeat, valid_days)

            # Too few arguments
            alarm_test.repeat = (True, True, True, True, True, True)
            self.assert_stderr(test_srderr)
            self.assertEqual(alarm_test.repeat, valid_days)

            # Wrong arguments
            alarm_test.repeat = (True, True, True, 0, True, True, True)
            self.assert_stderr(test_srderr)
            self.assertEqual(alarm_test.repeat, valid_days)

    def test_repeat_accessors_get(self):
        """
        Sets the repeat list at the constructor and variable level, and test
        that all the individual accessors for each day of the week works
        correctly.
        """
        days = [False, True, True, False, True, False, True]

        # Test constructor input
        alarm_test = AlarmItem(0, 0, days, False)
        self.assertEqual(alarm_test.repeat, tuple(days))
        self.assert_repeat(alarm_test, days)

        # Test repeat accesor with opposite repeat list
        for i in xrange(len(days)):
            days[i] = not days[i]
        alarm_test.repeat = days
        self.assertEqual(alarm_test.repeat, tuple(days))
        self.assert_repeat(alarm_test, days)

    def test_repeat_accessors_set(self):
        """
        Sets the repeat list and test that the individual set accessors work as
        expected, including throwing errors if values are not booleans.
        """
        alarm_test = AlarmItem(0, 0)
        days = [False, True, True, False, True, False, True]

        # Test with correct values
        alarm_test.monday = days[0]
        alarm_test.tuesday = days[1]
        alarm_test.wednesday = days[2]
        alarm_test.thursday = days[3]
        alarm_test.friday = days[4]
        alarm_test.saturday = days[5]
        alarm_test.sunday = days[6]
        self.assert_repeat(alarm_test, days)

        # To test the incorrect value, the accessor setter prints to stderr
        # if bad data is encountered, so we need to capture stderr to test it.
        with mock.patch('sys.stderr', new=io.StringIO()) as test_srderr:
            # First ensure that successful set does not write to stderr
            self.assertEqual(test_srderr.getvalue(), '')
            alarm_test.monday = days[0]
            self.assertEqual(test_srderr.getvalue(), '')

            # Monday
            alarm_test.monday = 'monday'
            self.assert_stderr(test_srderr)
            alarm_test.monday = 1
            self.assert_stderr(test_srderr)
            alarm_test.monday = 2.3
            self.assert_stderr(test_srderr)
            self.assertEqual(alarm_test.monday, days[0])

            # Tuesday
            alarm_test.tuesday = 'tuesday'
            self.assert_stderr(test_srderr)
            alarm_test.tuesday = 1
            self.assert_stderr(test_srderr)
            alarm_test.tuesday = 2.3
            self.assert_stderr(test_srderr)
            self.assertEqual(alarm_test.tuesday, days[1])

            # Wednesday
            alarm_test.wednesday = 'wednesday'
            self.assert_stderr(test_srderr)
            alarm_test.wednesday = 1
            self.assert_stderr(test_srderr)
            alarm_test.wednesday = 2.3
            self.assert_stderr(test_srderr)
            self.assertEqual(alarm_test.wednesday, days[2])

            # Thursday
            alarm_test.thursday = 'thursday'
            self.assert_stderr(test_srderr)
            alarm_test.thursday = 1
            self.assert_stderr(test_srderr)
            alarm_test.thursday = 2.3
            self.assert_stderr(test_srderr)
            self.assertEqual(alarm_test.thursday, days[3])

            # Friday
            alarm_test.friday = 'friday'
            self.assert_stderr(test_srderr)
            alarm_test.friday = 1
            self.assert_stderr(test_srderr)
            alarm_test.friday = 2.3
            self.assert_stderr(test_srderr)
            self.assertEqual(alarm_test.friday, days[4])

            # Saturday
            alarm_test.saturday = 'saturday'
            self.assert_stderr(test_srderr)
            alarm_test.saturday = 1
            self.assert_stderr(test_srderr)
            alarm_test.saturday = 2.3
            self.assert_stderr(test_srderr)
            self.assertEqual(alarm_test.saturday, days[5])

            # Sunday
            alarm_test.sunday = 'sunday'
            self.assert_stderr(test_srderr)
            alarm_test.sunday = 1
            self.assert_stderr(test_srderr)
            alarm_test.sunday = 2.3
            self.assertEqual(alarm_test.sunday, days[6])

    def test_id(self):
        """ Tests the id member variable accessors filters non-integers. """
        alarm_test = AlarmItem(0, 0)
        alarm_test.id_ = 5
        self.assertEqual(5, alarm_test.id_)

        # The accessor setter prints to stderr if bad data is encountered, so
        # we need to capture stderr to test it.
        with mock.patch('sys.stderr', new=io.StringIO()) as test_srderr:
            # First ensure that successful set does not write to stderr
            self.assertEqual(test_srderr.getvalue(), '')
            alarm_test.id_ = 10
            self.assertEqual(test_srderr.getvalue(), '')
            self.assertEqual(alarm_test.id_, 10)

            # Negative integer instead of positive integer
            alarm_test.id_ = -2
            self.assertEqual(alarm_test.id_, 10)
            self.assert_stderr(test_srderr)

            # String instead of integer
            alarm_test.id_ = 'String'
            self.assertEqual(alarm_test.id_, 10)
            self.assert_stderr(test_srderr)

            # Float instead of integer
            alarm_test.id_ = 10.4
            self.assertEqual(alarm_test.id_, 10)
            self.assert_stderr(test_srderr)

    def test_label(self):
        """ Tests the label variable accessors and its string coversion. """
        alarm_test = AlarmItem(0, 0)
        label = 'Alarm test label'

        # The accessor setter prints to stderr if bad data is encountered, so
        # we need to capture stderr to test it.
        with mock.patch('sys.stderr', new=io.StringIO()) as test_srderr:
            # First ensure that successful set does not write to stderr
            self.assertEqual(test_srderr.getvalue(), '')
            alarm_test.label = label
            self.assertEqual(label, alarm_test.label)
            self.assertEqual(test_srderr.getvalue(), '')

            # Try other types
            alarm_test.label = 5
            self.assertEqual('5', alarm_test.label)
            self.assertEqual(test_srderr.getvalue(), '')

            alarm_test.label = True
            self.assertEqual('True', alarm_test.label)
            self.assertEqual(test_srderr.getvalue(), '')

            alarm_test.label = {'test': 5}
            self.assertEqual("{u'test': 5}", alarm_test.label)
            self.assertEqual(test_srderr.getvalue(), '')

    def test_timestamp(self):
        """
        Tests the timetstamp member variable accessors filters non-integers.
        """
        alarm_test = AlarmItem(0, 0)
        alarm_test.timestamp = 1427486989
        self.assertEqual(alarm_test.timestamp, 1427486989)

        # The accessor setter prints to stderr if bad data is encountered, so
        # we need to capture stderr to test it.
        with mock.patch('sys.stderr', new=io.StringIO()) as test_srderr:
            # First ensure that successful set does not write to stderr
            self.assertEqual(test_srderr.getvalue(), '')
            alarm_test.timestamp = 10
            self.assertEqual(test_srderr.getvalue(), '')
            self.assertEqual(alarm_test.timestamp, 10)

            # Negative integer instead of positive integer
            alarm_test.timestamp = -2
            self.assertEqual(alarm_test.timestamp, 10)
            self.assert_stderr(test_srderr)

            # String instead of integer
            alarm_test.timestamp = 'String'
            self.assertEqual(alarm_test.timestamp, 10)
            self.assert_stderr(test_srderr)

            # Float instead of integer
            alarm_test.timestamp = 10.4
            self.assertEqual(alarm_test.timestamp, 10)
            self.assert_stderr(test_srderr)

    def test_time_to_alarm(self):
        """
        Full tests coverage for the get_time_diff function. Good resource:
        http://www.timeanddate.com/date/timeduration.html
        """
        one_day = 1440
        test_alarm = AlarmItem(
            9, 30, (True, False, False, True, False, False, False), True)
        time_diff = test_alarm.minutes_to_alert(9, 30, 0)
        self.assertEqual(time_diff, 0)
        time_diff = test_alarm.minutes_to_alert(9, 29, 0)
        self.assertEqual(time_diff, 1)
        time_diff = test_alarm.minutes_to_alert(19, 55, 2)
        self.assertEqual(time_diff, 815)
        time_diff = test_alarm.minutes_to_alert(9, 30, 2)
        self.assertEqual(time_diff, one_day)
        time_diff = test_alarm.minutes_to_alert(9, 30, 1)
        self.assertEqual(time_diff, (one_day * 2))
        time_diff = test_alarm.minutes_to_alert(9, 31, 1)
        self.assertEqual(time_diff, ((one_day * 2) - 1))
        time_diff = test_alarm.minutes_to_alert(9, 29, 4)
        self.assertEqual(time_diff, ((one_day * 3) + 1))
        time_diff = test_alarm.minutes_to_alert(3, 15, 1)
        self.assertEqual(time_diff, ((one_day * 2) + (60 * 6) + 15))

        test_alarm.repeat = (True, False, False, False, False, False, False)
        time_diff = test_alarm.minutes_to_alert(9, 31, 0)
        self.assertEqual(time_diff, ((one_day * 7) - 1))
        time_diff = test_alarm.minutes_to_alert(13, 34, 1)
        self.assertEqual(time_diff, ((one_day * 5) + (60 * 19) + 56))
        time_diff = test_alarm.minutes_to_alert(4, 15, 2)
        self.assertEqual(time_diff, ((one_day * 5) + (60 * 5) + 15))

    def test_string_alarm(self):
        """ Checks the __str__ output is correct. """
        test_alarm = AlarmItem(
            9, 30, (True, False, False, True, False, False, True), True)
        test_alarm.id_ = 10
        out = 'Alarm ID:  10 | Time: 09:30 | Enabled: Yes | Repeat: ' +\
              'Mon --- --- Thu --- --- Sun '
        self.assertEqual(str(test_alarm), out)

    def test_any_enabled_day(self):
        """ Test any_day_enabled() returns False if all repeats are false. """
        test_alarm = AlarmItem(
            9, 30, (True, False, False, True, False, False, True), True)
        self.assertTrue(test_alarm.any_day_enabled())
        test_alarm.repeat = (False, False, False, False, False, False, False)
        self.assertFalse(test_alarm.any_day_enabled())

    def test_diff_alarm(self):
        """ Tests the diff_alarm method returned Alarms. """
        # Helper function to assert the alarm properties, takes the outer scope
        # variables directly as we will be reusing them for all tests
        def assert_diff_alarm(diff_alarm):
            self.assertEqual(diff_alarm.minute, expected_minute)
            self.assertEqual(diff_alarm.hour, expected_hour)
            self.assert_repeat(diff_alarm, expected_days)
            self.assertEqual(diff_alarm.enabled, test_enabled)
            self.assertEqual(diff_alarm.label, expected_label)
            self.assertNotEqual(diff_alarm.timestamp, test_timestamp)
            self.assertNotEqual(diff_alarm.id_, test_id)

        # First test - 15 minutes to 9 30, so only change in minutes
        time_diff = -15
        test_minute = 30
        test_hour = 9
        expected_minute = 15
        expected_hour = 9
        test_days = (True, False, False, True, False, False, True)
        expected_days = test_days
        test_enabled = True
        test_id = 98
        test_label = "test label"
        expected_label = test_label + \
            (" (Alarm %s %+dmin)" % (test_id, time_diff))
        test_timestamp = 1234

        test_alarm = AlarmItem(
            test_hour, test_minute, days=test_days, enabled=test_enabled,
            timestamp=test_timestamp, label=test_label, alarm_id=test_id)
        assert_diff_alarm(test_alarm.diff_alarm(time_diff))

        # Now test + 15 minutes to 9 30, so only change in minutes
        time_diff = 15
        test_minute = 30
        test_hour = 9
        expected_minute = 45
        expected_hour = 9
        expected_label = test_label + \
            (" (Alarm %s %+dmin)" % (test_id, time_diff))

        test_alarm = AlarmItem(
            test_hour, test_minute, days=test_days, enabled=test_enabled,
            timestamp=test_timestamp, label=test_label, alarm_id=test_id)
        assert_diff_alarm(test_alarm.diff_alarm(time_diff))

        # Now test + 15 minutes to 9 30, so only change in minutes
        time_diff = 15
        test_minute = 30
        test_hour = 9
        expected_minute = 45
        expected_hour = 9
        expected_label = test_label + \
            (" (Alarm %s %+dmin)" % (test_id, time_diff))

        test_alarm = AlarmItem(
            test_hour, test_minute, days=test_days, enabled=test_enabled,
            timestamp=test_timestamp, label=test_label, alarm_id=test_id)
        assert_diff_alarm(test_alarm.diff_alarm(time_diff))

        # Now test + minutes with hour rollover
        time_diff = 59
        test_minute = 10
        test_hour = 14
        expected_minute = 9
        expected_hour = 15
        expected_label = test_label + \
            (" (Alarm %s %+dmin)" % (test_id, time_diff))

        test_alarm = AlarmItem(
            test_hour, test_minute, days=test_days, enabled=test_enabled,
            timestamp=test_timestamp, label=test_label, alarm_id=test_id)
        assert_diff_alarm(test_alarm.diff_alarm(time_diff))

        # Now test - minutes with hour rollover
        time_diff = -59
        test_minute = 10
        test_hour = 14
        expected_minute = 11
        expected_hour = 13
        expected_label = test_label + \
            (" (Alarm %s %+dmin)" % (test_id, time_diff))

        test_alarm = AlarmItem(
            test_hour, test_minute, days=test_days, enabled=test_enabled,
            timestamp=test_timestamp, label=test_label, alarm_id=test_id)
        assert_diff_alarm(test_alarm.diff_alarm(time_diff))

        # Now test + minutes with day rollover
        time_diff = 30
        test_minute = 50
        test_hour = 23
        expected_minute = 20
        expected_hour = 0
        test_days = (True, False, False, True, True, False, True)
        expected_days = (True, True, False, False, True, True, False)
        expected_label = test_label + \
            (" (Alarm %s %+dmin)" % (test_id, time_diff))

        test_alarm = AlarmItem(
            test_hour, test_minute, days=test_days, enabled=test_enabled,
            timestamp=test_timestamp, label=test_label, alarm_id=test_id)
        assert_diff_alarm(test_alarm.diff_alarm(time_diff))

        # Now test - minutes with day rollover
        time_diff = -30
        test_minute = 10
        test_hour = 0
        expected_minute = 40
        expected_hour = 23
        test_days = (True, False, False, True, True, False, True)
        expected_days = (False, False, True, True, False, True, True)
        expected_label = test_label + \
            (" (Alarm %s %+dmin)" % (test_id, time_diff))

        test_alarm = AlarmItem(
            test_hour, test_minute, days=test_days, enabled=test_enabled,
            timestamp=test_timestamp, label=test_label, alarm_id=test_id)
        assert_diff_alarm(test_alarm.diff_alarm(time_diff))

        # Test input sanitation capturing stderr to check
        with mock.patch('sys.stderr', new=io.StringIO()) as test_srderr:
            # First ensure that successful set does not write to stderr
            self.assertEqual(test_srderr.getvalue(), '')
            time_diff = 0
            test_alarm.diff_alarm(time_diff)
            self.assertEqual(test_srderr.getvalue(), '')

            # Lower boundary
            time_diff = -60
            test_alarm.diff_alarm(time_diff)
            self.assert_stderr(test_srderr)

            # Upper boundary
            time_diff = 60
            test_alarm.diff_alarm(time_diff)
            self.assert_stderr(test_srderr)

            # other types instead of integer
            time_diff = 0.1
            test_alarm.diff_alarm(time_diff)
            self.assert_stderr(test_srderr)
            time_diff = "0"
            test_alarm.diff_alarm(time_diff)
            self.assert_stderr(test_srderr)


if __name__ == '__main__':
    unittest.main()
