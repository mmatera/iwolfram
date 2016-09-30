import unittest
import jupyter_kernel_test

class MyKernelTests(jupyter_kernel_test.KernelTests):
    # Required --------------------------------------

    # The name identifying an installed kernel to run the tests against
    kernel_name = 'wolfram_kernel'

    # language_info.name in a kernel_info_reply should match this
    language_name = 'Mathematica'

    # language_info.file_extension, should match kernel_info_reply
    # (and start with a dot)
    file_extension = '.txt'

    # Optional --------------------------------------

    # Code in the kernel's language to write "hello, world" to stdout
    code_hello_world = 'Print["hello, world"]'

    # code which should print something to stderr
    code_stderr = '1/0'

    # Tab completions: in each dictionary, text is the input, which it will
    # try to complete from the end of. matches is the collection of results
    # it should expect.
    # TODO
    # completion_samples = []

    # Code completeness: samples grouped by expected result
    complete_code_samples = [
        'Sin[1/2]',
    ]
    incomplete_code_samples = [
        'Sin[1',
        '1 +',
        '"abc ',
    ]
    invalid_code_samples = [
        '{(1 + }2)',
    ]

    # Pager: code that should display something (anything) in the pager
    # TODO
    # code_page_something = "help('foldl')"

    # Code which the frontend should display an error for
    code_generate_error = "1/0"

    # Samples of code which generate a result value (ie, some text
    # displayed as Out[n])
    code_execute_result = [
        {'code': "1+2+4", 'result': "7"}
    ]

    # Samples of code which should generate a rich display output, and
    # the expected MIME type
    # TODO
    code_display_data = []

    # Which types of history access should be tested (omit this attribute
    # or use an empty list to test nothing). For history searching,
    # code_history_pattern should be a glob-type match for one of the
    # code strings in code_execute_result
    # TODO
    # supported_history_operations = ("tail", "range", "search")
    # code_history_pattern = "1?2*"

    # A statement/object to which the kernel should respond with some
    # information when inspected
    code_inspect_sample = "Sin"

    # Code which should cause the kernel to send a clear_output request
    # to the frontend
    # TODO
    # code_clear_output = "clear_output()"

if __name__ == '__main__':
    unittest.main()
