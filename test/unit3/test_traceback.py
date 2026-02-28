"""Tests for the traceback module."""

import sys
import traceback
import unittest


# create a fake io.Stream implementation
class StringIO:
    def __init__(self):
        self.buffer = []

    def write(self, text):
        self.buffer.append(str(text))

    def read(self):
        return ""

    def flush(self):
        pass

    def close(self):
        self.buffer = []

    def getvalue(self):
        return "".join(self.buffer)


def catch_error():
    try:
        raise ValueError("oops")
    except ValueError as e:
        return e


def catch_deep_error():
    def raise_value_error():
        raise ValueError("oops")

    def call_inner():
        raise_value_error()

    try:
        call_inner()
    except ValueError as e:
        return e


def normalise_lines(lines):
    return "".join(lines).splitlines()


class TracebackTest(unittest.TestCase):
    def test_exception_has_traceback_attr(self):
        e = catch_error()
        self.assertIsNotNone(e.__traceback__)

    def test_tb_lineno(self):
        e = catch_error()
        tb = e.__traceback__
        self.assertGreater(tb.tb_lineno, 0)

    def test_traceback_length(self):
        e = catch_deep_error()
        tb = e.__traceback__
        count = 0
        cur = tb
        while cur is not None:
            count += 1
            cur = cur.tb_next
        # Expect 3 frames: catch_value_error, call_inner, raise_value_error
        self.assertEqual(count, 3)


class SysExcInfoTest(unittest.TestCase):
    def test_sys_exc_info_inside_handler(self):
        try:
            raise ValueError("test")
        except ValueError:
            etype, val, tb = sys.exc_info()

        self.assertIs(etype, ValueError)
        self.assertIsInstance(val, ValueError)
        self.assertIsNotNone(tb)

    def test_sys_exc_info_from_caller(self):
        def check():
            etype, val, tb = sys.exc_info()
            self.assertIs(etype, ValueError)
            self.assertIsInstance(val, ValueError)
            self.assertIsNotNone(tb)

        try:
            raise ValueError("test")
        except ValueError:
            check()

    def test_sys_exc_info_outside_handler(self):
        etype, val, tb = sys.exc_info()
        self.assertIsNone(etype)
        self.assertIsNone(val)
        self.assertIsNone(tb)


class PrintTbTest(unittest.TestCase):
    def test_print_tb(self):
        e = catch_error()
        tb = e.__traceback__
        f = StringIO()
        traceback.print_tb(tb, file=f)
        lines = f.getvalue().splitlines()
        self.assertRegex(
            lines[0], '  File ".*test_traceback.py", line \d+, in catch_error'
        )
        self.assertEqual(lines[1], '    raise ValueError("oops")')
        self.assertEqual(len(lines), 2)

    def test_positive_limit(self):
        e = catch_deep_error()
        tb = e.__traceback__
        f = StringIO()
        traceback.print_tb(tb, limit=1, file=f)
        lines = f.getvalue().splitlines()
        self.assertRegex(
            lines[0], '  File ".*test_traceback.py", line \d+, in catch_deep_error'
        )
        self.assertEqual(lines[1], "    call_inner()")
        self.assertEqual(len(lines), 2)

    def test_negative_limit(self):
        e = catch_deep_error()
        tb = e.__traceback__
        f = StringIO()
        traceback.print_tb(tb, limit=-1, file=f)
        lines = f.getvalue().splitlines()
        self.assertRegex(
            lines[0], '  File ".*test_traceback.py", line \d+, in raise_value_error'
        )
        self.assertEqual(lines[1], '    raise ValueError("oops")')
        self.assertEqual(len(lines), 2)


class PrintExceptionTest(unittest.TestCase):
    def test_print_exception(self):
        e = catch_error()
        tb = e.__traceback__
        f = StringIO()
        traceback.print_exception(type(e), e, tb, file=f)
        lines = f.getvalue().splitlines()
        self.assertEqual(lines[0], "Traceback (most recent call last):")
        self.assertRegex(
            lines[1], '  File ".*test_traceback.py", line \d+, in catch_error'
        )
        self.assertEqual(lines[2], '    raise ValueError("oops")')
        self.assertEqual(lines[3], "ValueError: oops")
        self.assertEqual(len(lines), 4)

    def test_etype_arg_is_ignored(self):
        e = catch_error()
        tb = e.__traceback__
        f = StringIO()
        traceback.print_exception(SyntaxError, e, tb, file=f)
        lines = f.getvalue().splitlines()
        self.assertEqual(lines[3], "ValueError: oops")


class PrintExcTest(unittest.TestCase):
    def test_print_exc(self):
        try:
            raise ValueError("oops")
        except ValueError:
            f = StringIO()
            traceback.print_exc(file=f)

        lines = f.getvalue().splitlines()
        self.assertEqual(lines[0], "Traceback (most recent call last):")
        self.assertRegex(
            lines[1], '  File ".*test_traceback.py", line \d+, in test_print_exc'
        )
        self.assertEqual(lines[2], '    raise ValueError("oops")')
        self.assertEqual(lines[3], "ValueError: oops")
        self.assertEqual(len(lines), 4)

    def test_with_no_exception(self):
        f = StringIO()
        traceback.print_exc(file=f)
        lines = f.getvalue().splitlines()
        self.assertEqual(lines, ["NoneType: None"])


class ExtractTbTest(unittest.TestCase):
    def test_extract_tb(self):
        e = catch_deep_error()
        tb = e.__traceback__
        extracted = traceback.extract_tb(tb)
        self.assertEqual(len(extracted), 3)
        filename, lineno, name, line = extracted[0]
        self.assertIn("test_traceback.py", filename)
        self.assertGreater(lineno, 0)
        self.assertEqual(name, "catch_deep_error")
        self.assertEqual(line, "call_inner()")


class FormatListTest(unittest.TestCase):
    def test_format_list(self):
        e = catch_error()
        tb = e.__traceback__
        extracted = traceback.extract_tb(tb)
        lines = normalise_lines(traceback.format_list(extracted))
        self.assertRegex(
            lines[0], 'File ".*test_traceback.py", line \d+, in catch_error'
        )
        self.assertEqual(lines[1], '    raise ValueError("oops")')
        self.assertEqual(len(lines), 2)


class FormatExceptionOnlyTest(unittest.TestCase):
    def test_format_exception_only(self):
        e = catch_error()
        lines = traceback.format_exception_only(type(e), e)
        self.assertEqual(lines, ["ValueError: oops\n"])


class FormatExceptionTest(unittest.TestCase):
    def test_format_exception_has_header_and_traceback(self):
        e = catch_deep_error()
        lines = normalise_lines(traceback.format_exception(type(e), e, e.__traceback__))
        self.assertEqual(lines[0], "Traceback (most recent call last):")
        self.assertRegex(
            lines[1], 'File ".*test_traceback.py", line \d+, in catch_deep_error'
        )
        self.assertEqual(lines[2], "    call_inner()")
        self.assertRegex(
            lines[3], 'File ".*test_traceback.py", line \d+, in call_inner'
        )
        self.assertEqual(lines[4], "    raise_value_error()")
        self.assertRegex(
            lines[5], 'File ".*test_traceback.py", line \d+, in raise_value_error'
        )
        self.assertEqual(lines[6], '    raise ValueError("oops")')
        self.assertEqual(lines[7], "ValueError: oops")
        self.assertEqual(len(lines), 8)

    def test_format_exception_limit(self):
        e = catch_deep_error()
        lines = normalise_lines(
            traceback.format_exception(type(e), e, e.__traceback__, limit=1)
        )
        self.assertEqual(lines[0], "Traceback (most recent call last):")
        self.assertRegex(
            lines[1], 'File ".*test_traceback.py", line \d+, in catch_deep_error'
        )
        self.assertEqual(lines[2], "    call_inner()")
        self.assertEqual(lines[3], "ValueError: oops")
        self.assertEqual(len(lines), 4)

    def test_format_exception_none_tb_omits_header_and_traceback(self):
        e = catch_error()
        lines = traceback.format_exception(type(e), e, None)
        self.assertEqual(lines, ["ValueError: oops\n"])


class FormatExcTest(unittest.TestCase):
    def test_format_exc(self):
        try:
            raise ValueError("oops")
        except ValueError:
            text = traceback.format_exc()

        lines = text.splitlines()
        self.assertEqual(lines[0], "Traceback (most recent call last):")
        self.assertRegex(
            lines[1], 'File ".*test_traceback.py", line \d+, in test_format_exc'
        )
        self.assertEqual(lines[2], '    raise ValueError("oops")')
        self.assertEqual(lines[3], "ValueError: oops")
        self.assertEqual(len(lines), 4)


class FormatTbTest(unittest.TestCase):
    def test_format_tb(self):
        e = catch_error()
        tb = e.__traceback__
        lines = normalise_lines(traceback.format_tb(tb))
        self.assertRegex(
            lines[0], '  File ".*test_traceback.py", line \d+, in catch_error'
        )
        self.assertEqual(lines[1], '    raise ValueError("oops")')
        self.assertEqual(len(lines), 2)


class WalkTbTest(unittest.TestCase):
    def test_walk_stack(self):
        e = catch_deep_error()
        tb = e.__traceback__
        gen = traceback.walk_tb(tb)
        count = 0
        try:
            while True:
                next(gen)
                count += 1
        except StopIteration:
            pass
        # Expect 3 frames: catch_value_error, call_inner, raise_value_error
        self.assertEqual(count, 3)


if __name__ == "__main__":
    unittest.main()
