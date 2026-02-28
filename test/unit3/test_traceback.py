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

    def test_co_filename(self):
        e = catch_error()
        tb = e.__traceback__
        self.assertIn("test_traceback.py", tb.tb_frame.f_code.co_filename)

    def test_co_name(self):
        e = catch_error()
        tb = e.__traceback__
        self.assertEqual(tb.tb_frame.f_code.co_name, "catch_error")

    def test_co_firstlineno_is_def_line_not_raise_line(self):
        # co_firstlineno should be the 'def' line, which is less than
        # tb_lineno (the line where the exception was raised)
        e = catch_error()
        tb = e.__traceback__
        self.assertLess(tb.tb_frame.f_code.co_firstlineno, tb.tb_lineno)

    def test_f_lineno_is_at_least_tb_lineno(self):
        # If Skulpt had a live frame object, we would use it for f_lineno.
        # Since it doesn't, we set f_lineno to the line number of the traceback frame.
        e = catch_error()
        tb = e.__traceback__
        self.assertGreaterEqual(tb.tb_frame.f_lineno, tb.tb_lineno)

    def test_f_back_links_to_outer_frame(self):
        e = catch_deep_error()
        tb = e.__traceback__
        # inner frame's f_back points to the outer (calling) frame
        inner = tb.tb_next
        self.assertIsNotNone(inner.tb_frame.f_back)
        self.assertEqual(inner.tb_frame.f_back.f_code.co_name, tb.tb_frame.f_code.co_name)

    def test_nested_frames_have_correct_names(self):
        e = catch_deep_error()
        tb = e.__traceback__
        names = []
        while tb is not None:
            names.append(tb.tb_frame.f_code.co_name)
            tb = tb.tb_next
        self.assertEqual(names, ["catch_deep_error", "call_inner", "raise_value_error"])


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
        self.assertEqual(len(lines), 2)
        self.assertRegex(
            lines[0], r'  File ".*test_traceback\.py", line \d+, in catch_error'
        )
        self.assertEqual(lines[1], '    raise ValueError("oops")')

    def test_positive_limit(self):
        e = catch_deep_error()
        tb = e.__traceback__
        f = StringIO()
        traceback.print_tb(tb, limit=1, file=f)

        lines = f.getvalue().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertRegex(
            lines[0], r'  File ".*test_traceback\.py", line \d+, in catch_deep_error'
        )
        self.assertEqual(lines[1], "    call_inner()")

    def test_negative_limit(self):
        e = catch_deep_error()
        tb = e.__traceback__
        f = StringIO()
        traceback.print_tb(tb, limit=-1, file=f)

        lines = f.getvalue().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertRegex(
            lines[0], r'  File ".*test_traceback\.py", line \d+, in raise_value_error'
        )
        self.assertEqual(lines[1], '    raise ValueError("oops")')


class PrintExceptionTest(unittest.TestCase):
    def test_print_exception(self):
        e = catch_error()
        tb = e.__traceback__
        f = StringIO()
        traceback.print_exception(type(e), e, tb, file=f)

        lines = f.getvalue().splitlines()
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], "Traceback (most recent call last):")
        self.assertRegex(
            lines[1], r'  File ".*test_traceback\.py", line \d+, in catch_error'
        )
        self.assertEqual(lines[2], '    raise ValueError("oops")')
        self.assertEqual(lines[3], "ValueError: oops")

    def test_print_exception_with_chained_context(self):
        try:
            try:
                raise ValueError("original")
            except ValueError:
                raise RuntimeError("chained")
        except RuntimeError as e:
            f = StringIO()
            traceback.print_exception(type(e), e, e.__traceback__, file=f)

        lines = f.getvalue().splitlines()
        self.assertEqual(len(lines), 11)
        self.assertEqual(lines[0], "Traceback (most recent call last):")
        self.assertRegex(lines[1], r'  File ".*test_traceback\.py", line \d+, in test_print_exception_with_chained_context')
        self.assertEqual(lines[2], '    raise ValueError("original")')
        self.assertEqual(lines[3], "ValueError: original")
        self.assertEqual(lines[4], "")
        self.assertEqual(lines[5], "During handling of the above exception, another exception occurred:")
        self.assertEqual(lines[6], "")
        self.assertEqual(lines[7], "Traceback (most recent call last):")
        self.assertRegex(lines[8], r'  File ".*test_traceback\.py", line \d+, in test_print_exception_with_chained_context')
        self.assertEqual(lines[9], '    raise RuntimeError("chained")')
        self.assertEqual(lines[10], "RuntimeError: chained")

    def test_print_exception_chain_false_suppresses_context(self):
        try:
            try:
                raise ValueError("original")
            except ValueError:
                raise RuntimeError("chained")
        except RuntimeError as e:
            f = StringIO()
            traceback.print_exception(type(e), e, e.__traceback__, chain=False, file=f)

        lines = f.getvalue().splitlines()
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], "Traceback (most recent call last):")
        self.assertRegex(lines[1], r'  File ".*test_traceback\.py", line \d+, in test_print_exception_chain_false_suppresses_context')
        self.assertEqual(lines[2], '    raise RuntimeError("chained")')
        self.assertEqual(lines[3], "RuntimeError: chained")

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
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], "Traceback (most recent call last):")
        self.assertRegex(
            lines[1], r'  File ".*test_traceback\.py", line \d+, in test_print_exc'
        )
        self.assertEqual(lines[2], '    raise ValueError("oops")')
        self.assertEqual(lines[3], "ValueError: oops")

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

        self.assertEqual(len(lines), 2)
        self.assertRegex(
            lines[0], r'File ".*test_traceback\.py", line \d+, in catch_error'
        )
        self.assertEqual(lines[1], '    raise ValueError("oops")')


class FormatExceptionOnlyTest(unittest.TestCase):
    def test_format_exception_only(self):
        e = catch_error()
        lines = traceback.format_exception_only(type(e), e)
        self.assertEqual(lines, ["ValueError: oops\n"])


class FormatExceptionTest(unittest.TestCase):
    def test_format_exception_has_header_and_traceback(self):
        e = catch_deep_error()
        lines = normalise_lines(traceback.format_exception(type(e), e, e.__traceback__))

        self.assertEqual(len(lines), 8)
        self.assertEqual(lines[0], "Traceback (most recent call last):")
        self.assertRegex(
            lines[1], r'File ".*test_traceback\.py", line \d+, in catch_deep_error'
        )
        self.assertEqual(lines[2], "    call_inner()")
        self.assertRegex(
            lines[3], r'File ".*test_traceback\.py", line \d+, in call_inner'
        )
        self.assertEqual(lines[4], "    raise_value_error()")
        self.assertRegex(
            lines[5], r'File ".*test_traceback\.py", line \d+, in raise_value_error'
        )
        self.assertEqual(lines[6], '    raise ValueError("oops")')
        self.assertEqual(lines[7], "ValueError: oops")

    def test_format_exception_limit(self):
        e = catch_deep_error()
        lines = normalise_lines(
            traceback.format_exception(type(e), e, e.__traceback__, limit=1)
        )

        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], "Traceback (most recent call last):")
        self.assertRegex(
            lines[1], r'File ".*test_traceback\.py", line \d+, in catch_deep_error'
        )
        self.assertEqual(lines[2], "    call_inner()")
        self.assertEqual(lines[3], "ValueError: oops")

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
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], "Traceback (most recent call last):")
        self.assertRegex(
            lines[1], r'File ".*test_traceback\.py", line \d+, in test_format_exc'
        )
        self.assertEqual(lines[2], '    raise ValueError("oops")')
        self.assertEqual(lines[3], "ValueError: oops")


class FormatTbTest(unittest.TestCase):
    def test_format_tb(self):
        e = catch_error()
        tb = e.__traceback__
        lines = normalise_lines(traceback.format_tb(tb))

        self.assertEqual(len(lines), 2)
        self.assertRegex(
            lines[0], r'  File ".*test_traceback\.py", line \d+, in catch_error'
        )
        self.assertEqual(lines[1], '    raise ValueError("oops")')


class WalkTbTest(unittest.TestCase):
    def test_walk_tb(self):
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


class ExceptionContextTest(unittest.TestCase):
    def test_context_set_when_raised_inside_except(self):
        try:
            try:
                raise ValueError("original")
            except ValueError:
                raise RuntimeError("new")
        except RuntimeError as e:
            self.assertIsInstance(e.__context__, ValueError)
            self.assertEqual(str(e.__context__), "original")

    def test_context_is_none_when_not_in_handler(self):
        try:
            raise ValueError("standalone")
        except ValueError as e:
            self.assertIsNone(e.__context__)

    def test_context_chained_three_levels(self):
        try:
            try:
                try:
                    raise ValueError("first")
                except ValueError:
                    raise TypeError("second")
            except TypeError:
                raise RuntimeError("third")
        except RuntimeError as e:
            self.assertIsInstance(e.__context__, TypeError)
            self.assertIsInstance(e.__context__.__context__, ValueError)

    def test_bare_reraise_does_not_set_context(self):
        try:
            try:
                raise ValueError("original")
            except ValueError:
                raise  # bare re-raise
        except ValueError as e:
            self.assertIsNone(e.__context__)


class RaiseFromTest(unittest.TestCase):
    def test_raise_from_sets_cause_and_suppress_context(self):
        try:
            try:
                raise ValueError("original")
            except ValueError as orig:
                raise RuntimeError("chained") from orig
        except RuntimeError as e:
            self.assertIsInstance(e.__cause__, ValueError)
            self.assertTrue(e.__suppress_context__)

    def test_raise_from_none_sets_suppress_context(self):
        try:
            try:
                raise ValueError("original")
            except ValueError:
                raise RuntimeError("suppressed") from None
        except RuntimeError as e:
            self.assertIsNone(e.__cause__)
            self.assertTrue(e.__suppress_context__)

    def test_raise_from_prints_direct_cause_message(self):
        try:
            try:
                raise ValueError("original")
            except ValueError as orig:
                raise RuntimeError("chained") from orig
        except RuntimeError as e:
            f = StringIO()
            traceback.print_exception(type(e), e, e.__traceback__, file=f)

        lines = f.getvalue().splitlines()
        self.assertEqual(len(lines), 11)
        self.assertEqual(lines[0], "Traceback (most recent call last):")
        self.assertRegex(lines[1], r'  File ".*test_traceback\.py", line \d+, in test_raise_from_prints_direct_cause_message')
        self.assertEqual(lines[2], '    raise ValueError("original")')
        self.assertEqual(lines[3], "ValueError: original")
        self.assertEqual(lines[4], "")
        self.assertEqual(lines[5], "The above exception was the direct cause of the following exception:")
        self.assertEqual(lines[6], "")
        self.assertEqual(lines[7], "Traceback (most recent call last):")
        self.assertRegex(lines[8], r'  File ".*test_traceback\.py", line \d+, in test_raise_from_prints_direct_cause_message')
        self.assertEqual(lines[9], '    raise RuntimeError("chained") from orig')
        self.assertEqual(lines[10], "RuntimeError: chained")

    def test_raise_from_none_suppresses_context_in_output(self):
        try:
            try:
                raise ValueError("original")
            except ValueError:
                raise RuntimeError("suppressed") from None
        except RuntimeError as e:
            f = StringIO()
            traceback.print_exception(type(e), e, e.__traceback__, file=f)

        lines = f.getvalue().splitlines()
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], "Traceback (most recent call last):")
        self.assertRegex(lines[1], r'  File ".*test_traceback\.py", line \d+, in test_raise_from_none_suppresses_context_in_output')
        self.assertEqual(lines[2], '    raise RuntimeError("suppressed") from None')
        self.assertEqual(lines[3], "RuntimeError: suppressed")


if __name__ == "__main__":
    unittest.main()
