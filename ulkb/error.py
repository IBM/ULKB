# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from . import util


class Error(Exception):
    def __init__(self, msg=None):
        super().__init__(self, msg)
        self.msg = msg

    def __str__(self):
        return self.msg


def _build_bad_argument_message(
        arg, msg_start, msg_end=None,
        func_name=None, arg_name=None, arg_position=None):
    msg = [msg_start]
    if arg_name and arg_position:
        msg.append(f"#{arg_position} ({arg_name}={arg})")
    elif arg_position:
        msg.append(f"#{arg_position} ({arg})")
    elif arg_name:
        msg.append(f"'{arg_name}' ({arg})")
    else:
        msg.append(f'({arg})')
    if func_name:
        msg.append(f"to '{func_name}'")
    if msg_end:
        msg.append(msg_end)
    return ' '.join(msg)


def _build_plural_message(msg, arg, *args, replace='s'):
    if not args:
        if replace:
            msg %= ''
        return f"{msg} '{arg}'"
    else:
        if replace:
            msg %= replace
        args = ', '.join(map(
            lambda x: f"'{x}'", sorted(map(str, util.chain([arg], args)))))
        return f"{msg}: {args}"


def arg_error(
        arg, extra_msg=None, func_name=None, arg_name=None,
        arg_position=None, exception=None):
    msg = _build_bad_argument_message(
        arg, 'bad argument', f'({extra_msg})' if extra_msg else None,
        func_name, arg_name, arg_position)
    exception = exception if exception is not None else ValueError
    raise exception(msg)


def check_arg(
        arg, test, extra_msg=None, func_name=None, arg_name=None,
        arg_position=None, exception=None):
    if test(arg) if callable(test) else test:
        return arg
    else:
        arg_error(
            arg, extra_msg, func_name, arg_name, arg_position, exception)


def check_optional_arg(
        arg, test, default, extra_msg=None, func_name=None, arg_name=None,
        arg_position=None, exception=None):
    if arg is None:
        return default
    else:
        return check_arg(
            arg, test, extra_msg,
            func_name, arg_name, arg_position, exception)


def check_arg_is_callable(
        arg, func_name=None, arg_name=None, arg_position=None):
    return check_arg(
        arg, callable(arg), 'expected callable',
        func_name, arg_name, arg_position)


def check_arg_is_none(
        arg, func_name=None, arg_name=None, arg_position=None):
    return check_arg(
        arg, arg is None, 'expected None',
        func_name, arg_name, arg_position, TypeError)


def check_arg_is_not_none(
        arg, func_name=None, arg_name=None, arg_position=None):
    return check_arg(
        arg, arg is not None, 'expected value, got None',
        func_name, arg_name, arg_position, TypeError)


def check_arg_is_type(
        arg, func_name=None, arg_name=None, arg_position=None):
    return check_arg(
        arg, isinstance(arg, type),
        f'expected type, got {type(arg).__name__}',
        func_name, arg_name, arg_position, TypeError)


def check_arg_enum(
        arg, enum, func_name=None, arg_name=None, arg_position=None):
    if arg in enum:
        return arg
    else:
        msg = _build_plural_message('expected', *enum, replace=False)
        return arg_error(
            arg, msg, func_name, arg_name, arg_position)


def check_optional_arg_enum(
        arg, enum, default, func_name=None, arg_name=None,
        arg_position=None):
    if arg is None:
        return default
    else:
        return check_arg_enum(arg, enum, func_name, arg_name, arg_position)


def check_arg_class(
        arg, cls, func_name=None, arg_name=None, arg_position=None):
    return check_arg_class_test(
        arg, cls, isinstance(arg, cls), func_name, arg_name, arg_position)


def check_arg_class_test(
        arg, cls, test, func_name=None, arg_name=None, arg_position=None):
    if test:
        return arg
    else:
        expected, got = cls, type(arg)
        if hasattr(expected, '__name__'):
            expected = expected.__name__
        if hasattr(got, '__name__'):
            got = got.__name__
        return arg_error(
            arg, f'expected {expected}, got {got}',
            func_name, arg_name, arg_position, TypeError)


def should_not_get_here(extra_msg=None, msg='should not get here'):
    if extra_msg:
        raise RuntimeError(f'{msg}: {extra_msg}')
    else:
        raise RuntimeError(msg)
