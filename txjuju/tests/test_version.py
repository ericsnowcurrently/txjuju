# Copyright 2016 Canonical Limited.  All rights reserved.

import unittest

from txjuju.version import VersionNumber, Version


class VersionNumberTest(unittest.TestCase):

    def test_parse_with_micro(self):
        ver = VersionNumber.parse("1.2.3")

        self.assertEqual(ver, VersionNumber(1, 2, 3))

    def test_parse_without_micro(self):
        ver = VersionNumber.parse("1.2")

        self.assertEqual(ver, VersionNumber(1, 2))

    def test_parse_without_minor(self):
        with self.assertRaises(ValueError):
            VersionNumber.parse("1")

    def test_parse_blank(self):
        with self.assertRaises(ValueError):
            VersionNumber.parse("")

    def test_parse_with_whitespace(self):
        ver = VersionNumber.parse(" 1.2.3 ")

        self.assertEqual(ver, VersionNumber(1, 2, 3))

    def test_parse_micro_wildcard(self):
        for verstr in (
                "1.2.x",
                "1.2.X",
                "1.2.*",
                ):
            ver = VersionNumber.parse(verstr)

            self.assertEqual(ver, VersionNumber(1, 2, "x"))

    def test_parse_minor_wildcard_without_micro(self):
        for verstr in (
                "1.x",
                "1.X",
                "1.*",
                ):
            ver = VersionNumber.parse(verstr)

            self.assertEqual(ver, VersionNumber(1, "x"))

    def test_parse_minor_wildcard_with_micro(self):
        with self.assertRaises(ValueError):
            VersionNumber.parse("1.*.3")

    def test_parse_major_wildcard(self):
        with self.assertRaises(ValueError):
            VersionNumber.parse("*")

    def test_parse_missing_major(self):
        with self.assertRaises(ValueError):
            VersionNumber.parse(".2.3")

    def test_parse_missing_minor(self):
        with self.assertRaises(ValueError):
            VersionNumber.parse("1..3")

    def test_parse_missing_micro(self):
        with self.assertRaises(ValueError):
            VersionNumber.parse("1.2.")

    def test_parse_not_number(self):
        for verstr in (
                "XXX.2.3",
                "1.XXX.3",
                "1.2.XXX",
                ):
            with self.assertRaises(ValueError):
                VersionNumber.parse(verstr)

    def test_parse_negative_number(self):
        for verstr in (
                "-1.2.3",
                "1.-2.3",
                "1.2.-3",
                ):
            with self.assertRaises(ValueError):
                VersionNumber.parse(verstr)

    def test_with_micro(self):
        ver = VersionNumber(1, 2, 3)

        self.assertEqual(ver.major, 1)
        self.assertEqual(ver.minor, 2)
        self.assertEqual(ver.micro, 3)

    def test_without_micro(self):
        ver = VersionNumber(1, 2)

        self.assertEqual(ver.major, 1)
        self.assertEqual(ver.minor, 2)
        self.assertIs(ver.micro, None)
        self.assertEqual(ver, VersionNumber(1, 2, None))

    def test_zero_micro(self):
        ver1 = VersionNumber(1, 2, 0)
        ver2 = VersionNumber(1, 2)

        self.assertNotEqual(ver1, ver2)

    def test_convert_from_string(self):
        ver = VersionNumber("1", "2", "3")

        self.assertEqual(ver.major, 1)
        self.assertEqual(ver.minor, 2)
        self.assertEqual(ver.micro, 3)

    def test_micro_wildcard(self):
        for ver in (
                VersionNumber(1, 2, "x"),
                VersionNumber(1, 2, "X"),
                VersionNumber(1, 2, "*"),
                ):
            self.assertEqual(ver.major, 1)
            self.assertEqual(ver.minor, 2)
            self.assertEqual(ver.micro, "x")

    def test_minor_wildcard_without_micro(self):
        for ver in (
                VersionNumber(1, "x"),
                VersionNumber(1, "X"),
                VersionNumber(1, "*"),
                ):
            self.assertEqual(ver.major, 1)
            self.assertEqual(ver.minor, "x")
            self.assertIs(ver.micro, None)

    def test_minor_wildcard_with_micro(self):
        with self.assertRaises(ValueError):
            VersionNumber(1, "*", 3)

    def test_missing_major(self):
        with self.assertRaises(ValueError):
            VersionNumber(None, 2, 3)

    def test_missing_minor(self):
        with self.assertRaises(ValueError):
            VersionNumber(1, None, 3)

    def test_missing_micro(self):
        ver = VersionNumber(1, 2, None)

        self.assertEqual(ver.major, 1)
        self.assertEqual(ver.minor, 2)
        self.assertIs(ver.micro, None)

    def test_not_number(self):
        for args in (
                ("XXX", 2, 3),
                (1, "XXX", 3),
                (1, 2, "XXX"),
                ):
            with self.assertRaises(ValueError):
                VersionNumber(*args)

    def test_negative_number(self):
        for args in (
                (-1, 2, 3),
                (1, -2, 3),
                (1, 2, -3),
                ):
            with self.assertRaises(ValueError):
                VersionNumber(*args)

    def test_all_zero(self):
        with self.assertRaises(ValueError):
            VersionNumber(0, 0, 0)

    def test_str_with_micro(self):
        ver = VersionNumber(1, 2, 3)
        verstr = str(ver)

        self.assertEqual(verstr, "1.2.3")

    def test_str_without_micro(self):
        ver = VersionNumber(1, 2)
        verstr = str(ver)

        self.assertEqual(verstr, "1.2")

    def test_is_wildcard(self):
        self.assertTrue(VersionNumber(1, 2).iswildcard)
        self.assertTrue(VersionNumber(1, 2, "*").iswildcard)
        self.assertTrue(VersionNumber(1, "*").iswildcard)

        self.assertFalse(VersionNumber(1, 2, 3).iswildcard)

    def test_match_micro_wildcard_positive(self):
        expected = VersionNumber(1, 2, "x")
        ver = VersionNumber(1, 2, 3)
        matched = expected.match(ver)

        self.assertTrue(matched)

    def test_match_micro_wildcard_negative(self):
        expected = VersionNumber(1, 2, "x")
        ver = VersionNumber(0, 2, 3)
        matched = expected.match(ver)

        self.assertFalse(matched)

    def test_match_missing_micro_positive(self):
        expected = VersionNumber(1, 2)
        ver = VersionNumber(1, 2, 3)
        matched = expected.match(ver)

        self.assertTrue(matched)

    def test_match_missing_micro_negative(self):
        expected = VersionNumber(1, 2)
        ver = VersionNumber(0, 2, 3)
        matched = expected.match(ver)

        self.assertFalse(matched)

    def test_match_minor_wildcard_positive(self):
        expected = VersionNumber(1,"x")
        ver = VersionNumber(1, 2, 3)
        matched = expected.match(ver)

        self.assertTrue(matched)

    def test_match_minor_wildcard_negative(self):
        expected = VersionNumber(1, "x")
        ver = VersionNumber(2, 0, 1)
        matched = expected.match(ver)

        self.assertFalse(matched)

    def test_match_equal(self):
        expected = VersionNumber(1, 2, 3)
        ver = VersionNumber(1, 2, 3)
        matched = expected.match(ver)

        self.assertTrue(matched)

    def test_match_identity(self):
        ver = VersionNumber(1, 2, 3)
        matched = ver.match(ver)

        self.assertTrue(matched)


class VersionTest(unittest.TestCase):

    def test_parse_full_micro_final(self):
        ver = Version.parse("1.2.3-xenial-amd64")

        num = VersionNumber(1, 2, 3)
        self.assertEqual(ver, Version(num, "final", "xenial", "amd64"))

    def test_parse_full_initial_final(self):
        ver = Version.parse("1.2.0-xenial-amd64")

        num = VersionNumber(1, 2, 0)
        self.assertEqual(ver, Version(num, "final", "xenial", "amd64"))

    def test_parse_full_micro_dev(self):
        ver = Version.parse("1.2.3-beta2-xenial-amd64")

        num = VersionNumber(1, 2, 3)
        self.assertEqual(ver, Version(num, "beta2", "xenial", "amd64"))

    def test_parse_full_initial_dev(self):
        ver = Version.parse("1.2-beta2-xenial-amd64")

        num = VersionNumber(1, 2, 0)
        self.assertEqual(ver, Version(num, "beta2", "xenial", "amd64"))

    def test_parse_micro_final(self):
        ver = Version.parse("1.2.3")

        num = VersionNumber(1, 2, 3)
        self.assertEqual(ver, Version(num, "final"))

    def test_parse_initial_final(self):
        ver = Version.parse("1.2.0")

        num = VersionNumber(1, 2, 0)
        self.assertEqual(ver, Version(num, "final"))

    def test_parse_micro_dev(self):
        ver = Version.parse("1.2.3-beta2")

        num = VersionNumber(1, 2, 3)
        self.assertEqual(ver, Version(num, "beta2"))

    def test_parse_initial_dev(self):
        ver = Version.parse("1.2-beta2")

        num = VersionNumber(1, 2, 0)
        self.assertEqual(ver, Version(num, "beta2"))

    def test_parse_superflous_micro(self):
        ver = Version.parse("1.2.0-beta2-xenial-amd64")

        num = VersionNumber(1, 2, 0)
        self.assertEqual(ver, Version(num, "beta2", "xenial", "amd64"))

    def test_parse_superflous_final(self):
        ver = Version.parse("1.2.0-final-xenial-amd64")

        num = VersionNumber(1, 2, 0)
        self.assertEqual(ver, Version(num, "final", "xenial", "amd64"))

    def test_parse_wildcard(self):
        with self.assertRaises(ValueError):
            Version.parse("1.2-xenial-amd64")

    def test_with_all_args(self):
        num = VersionNumber(1, 2, 3)
        ver = Version(num, "beta3", "xenial", "amd64")

        self.assertEqual(ver.number, num)
        self.assertEqual(ver.releaselevel, "beta3")
        self.assertEqual(ver.series, "xenial")
        self.assertEqual(ver.arch, "amd64")

    def test_minimal_args(self):
        num = VersionNumber(1, 2, 3)
        ver = Version(num)

        self.assertEqual(ver.number, num)
        self.assertEqual(ver.releaselevel, "final")
        self.assertIs(ver.series, None)
        self.assertIs(ver.arch, None)

    def test_number_string(self):
        ver = Version("1.2.3", "beta3", "xenial", "amd64")

        self.assertEqual(ver.number, VersionNumber(1, 2, 3))
        self.assertEqual(ver.releaselevel, "beta3")
        self.assertEqual(ver.series, "xenial")
        self.assertEqual(ver.arch, "amd64")

    def test_force_lowercase(self):
        num = VersionNumber(1, 2, 3)
        ver = Version(num, "BETA3", "XENIAL", "AMD64")

        self.assertEqual(ver.releaselevel, "beta3")
        self.assertEqual(ver.series, "xenial")
        self.assertEqual(ver.arch, "amd64")

    def test_force_None(self):
        num = VersionNumber(1, 2, 3)
        ver = Version(num, "", "", "")

        self.assertEqual(ver.releaselevel, "final")
        self.assertIs(ver.series, None)
        self.assertIs(ver.arch, None)

    def test_missing_number(self):
        with self.assertRaises(ValueError):
            Version(None, "beta3", "xenial", "amd64")

    def test_wildcard(self):
        num = VersionNumber(1, 2, "x")
        with self.assertRaises(ValueError):
            Version(num, "beta3", "xenial", "amd64")

    def test_invalid_releaselevel(self):
        num = VersionNumber(1, 2, 3)
        with self.assertRaises(ValueError):
            Version(num, "???", "xenial", "amd64")

    def test_unsupported_releaselevel(self):
        num = VersionNumber(1, 2, 3)
        with self.assertRaises(ValueError):
            Version(num, "canary1", "xenial", "amd64")

    def test_missing_series(self):
        num = VersionNumber(1, 2, 3)
        with self.assertRaises(ValueError):
            Version(num, "beta3", arch="amd64")

    @unittest.skip("not implemented yet")
    def test_invalid_series(self):
        num = VersionNumber(1, 2, 3)
        with self.assertRaises(ValueError):
            Version(num, "beta3", "???", "amd64")

    @unittest.skip("not implemented yet")
    def test_unsupported_series(self):
        num = VersionNumber(1, 2, 3)
        with self.assertRaises(ValueError):
            Version(num, "beta3", "spicy", "amd64")

    def test_missing_arch(self):
        num = VersionNumber(1, 2, 3)
        with self.assertRaises(ValueError):
            Version(num, "beta3", "xenial")

    @unittest.skip("not implemented yet")
    def test_invalid_arch(self):
        num = VersionNumber(1, 2, 3)
        with self.assertRaises(ValueError):
            Version(num, "beta3", "xenial", "???")

    @unittest.skip("not implemented yet")
    def test_unsupported_arch(self):
        num = VersionNumber(1, 2, 3)
        with self.assertRaises(ValueError):
            Version(num, "beta3", "xenial", "cell")

    def test_str_full_micro_final(self):
        num = VersionNumber(1, 2, 3)
        ver = Version(num, "final", "xenial", "amd64")
        verstr = str(ver)

        self.assertEqual(verstr, "1.2.3-xenial-amd64")

    def test_str_full_initial_final(self):
        num = VersionNumber(1, 2, 0)
        ver = Version(num, "final", "xenial", "amd64")
        verstr = str(ver)

        self.assertEqual(verstr, "1.2.0-xenial-amd64")

    def test_str_full_micro_dev(self):
        num = VersionNumber(1, 2, 3)
        ver = Version(num, "beta2", "xenial", "amd64")
        verstr = str(ver)

        self.assertEqual(verstr, "1.2.3-beta2-xenial-amd64")

    def test_str_full_initial_dev(self):
        num = VersionNumber(1, 2, 0)
        ver = Version(num, "beta2", "xenial", "amd64")
        verstr = str(ver)

        self.assertEqual(verstr, "1.2-beta2-xenial-amd64")

    def test_str_micro_final(self):
        num = VersionNumber(1, 2, 3)
        ver = Version(num, "final")
        verstr = str(ver)

        self.assertEqual(verstr, "1.2.3")

    def test_str_micro_dev(self):
        num = VersionNumber(1, 2, 3)
        ver = Version(num, "beta2")
        verstr = str(ver)

        self.assertEqual(verstr, "1.2.3-beta2")

    def test_str_initial_dev(self):
        num = VersionNumber(1, 2, 0)
        ver = Version(num, "beta2")
        verstr = str(ver)

        self.assertEqual(verstr, "1.2-beta2")
