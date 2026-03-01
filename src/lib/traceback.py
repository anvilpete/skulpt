import linecache
import sys

import _sk_fail


def extract_tb(tb, limit=None):
    result = []
    while tb is not None:
        item = (
            tb.tb_frame.f_code.co_filename,
            tb.tb_lineno,
            tb.tb_frame.f_code.co_name,
            linecache.getline(tb.tb_frame.f_code.co_filename, tb.tb_lineno).strip() or None,
        )
        result.append(item)
        tb = tb.tb_next

    if limit is None:
        return result
    if limit >= 0:
        return result[:limit]
    else:
        return result[limit:]


def extract_stack(limit=None):
    _sk_fail._("traceback.extract_stack")


def format_list(extracted_list):
    lines = []
    for filename, lineno, name, line in extracted_list:
        text = '  File "{}", line {}, in {}\n'.format(filename, lineno, name)
        if line is not None:
            text += "    {}\n".format(line)
        lines.append(text)
    return lines


def format_exception_only(etype, value):
    type_name = etype.__name__
    msg = str(value)
    return ["{}: {}\n".format(type_name, msg) if msg else "{}\n".format(type_name)]


def format_exception(etype, value, tb, limit=None, chain=True):
    lines = []
    if tb is not None:
        lines.append("Traceback (most recent call last):\n")
        lines += format_list(extract_tb(tb, limit))
    lines += format_exception_only(type(value), value)
    return lines


def format_exc(limit=None, chain=True):
    return "".join(format_exception(*sys.exc_info(), limit, chain))


def format_tb(tb, limit=None):
    return format_list(extract_tb(tb, limit))


def format_stack(f=None, limit=None):
    _sk_fail._("traceback.format_stack")


def print_tb(tb, limit=None, file=None):
    if file is None:
        file = sys.stderr
    for line in format_list(extract_tb(tb, limit)):
        file.write(line)


def print_exception(etype, value, tb, limit=None, file=None, chain=True):
    if file is None:
        file = sys.stderr
    for line in format_exception(etype, value, tb, limit, chain):
        file.write(line)


def print_exc(limit=None, file=None, chain=True):
    print_exception(*sys.exc_info(), limit, file, chain)


def print_last(limit=None, file=None, chain=True):
    _sk_fail._("traceback.print_last")


def print_stack(limit=None, file=None):
    _sk_fail._("traceback.print_stack")


def clear_frames(tb):
    _sk_fail._("traceback.clear_frames")


def walk_stack(tb):
    _sk_fail._("traceback.walk_stack")


def walk_tb(tb):
    while tb is not None:
        yield tb, tb.tb_lineno
        tb = tb.tb_next
    raise StopIteration
