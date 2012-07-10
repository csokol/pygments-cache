import unittest
from cache import *

class PygmentsCacheTest(unittest.TestCase): 

    def test_verify_input_file_argument(self):
        cache = PygmentizeCache(['pygmentize', '-o', 'output', 'input.html'], PygmentizeExecutor())
        self.assertTrue(cache.contains_input_file())
        
    def test_verify_stdin_argument(self):
        cache = PygmentizeCache(['pygmentize', '-o', 'output'], PygmentizeExecutor())
        self.assertFalse(cache.contains_input_file())
        
    def test_verify_pygmentize_args_parse(self):
        cache = PygmentizeCache(['pygmentize', '-f', 'latex', '-o', 'output', 'index.html'], PygmentizeExecutor())
        pygmentize_cmd = cache.parse_pygmentizeargs()
        self.assertEqual(pygmentize_cmd, 'pygmentize -f latex -o output index.html')
        
    def test_find_output_filename(self):
        cache = PygmentizeCache(['pygmentize', '-f', 'latex', '-o', 'output', 'index.html'], PygmentizeExecutor())
        outputfilename = cache.find_output_filename()
        self.assertEqual(outputfilename, 'output')
        