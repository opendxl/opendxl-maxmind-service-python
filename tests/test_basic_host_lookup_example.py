import sys
import unittest

if sys.version_info[0] > 2:
    import builtins # pylint: disable=import-error, unused-import
else:
    import __builtin__ # pylint: disable=import-error
    builtins = __builtin__ # pylint: disable=invalid-name

# pylint: disable=wrong-import-position
from mock import patch
import dxlmaxmindservice

class StringMatches(str):
    def __eq__(self, other):
        return self in other


class StringDoesNotMatch(str):
    def __eq__(self, other):
        return self not in other


class BasicHostLookupExample(unittest.TestCase):
    def test_basic_host_lookup_example(self): # pylint: disable=no-self-use
        sample_file = "sample/basic/basic_host_lookup_example.py"
        sample_globals = {"__file__": sample_file}
        with dxlmaxmindservice.MaxMindGeolocationService("config") as app:
            app.run()
            with open(sample_file) as f, \
                patch.object(builtins, 'print') as mock_print:
                exec(f.read(), sample_globals) # pylint: disable=exec-used
        mock_print.assert_called_with(StringMatches("registered_country"))
        mock_print.assert_called_with(
            StringDoesNotMatch("Error invoking service"))
