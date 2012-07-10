#!/usr/bin/python

import sys, hashlib, os, shlex, time, shutil, traceback
from subprocess import Popen, PIPE, STDOUT
import sys
from pkg_resources import load_entry_point
                                                                                                                                                                                                
CACHE_DIR = os.getenv("HOME") + "/.pygments/cache/"

def log(string):
    log = open('/tmp/pygmentize-output', 'a')
    log.write(string + "\n")
    log.close

class CacheManipulator():
    def sourcecode_md5(self, sourcecode, pygmentize_cmd):
        md5 = hashlib.md5()
        md5.update(sourcecode + pygmentize_cmd)
        return md5.hexdigest()
        
    def find(self, code_to_pygmentize, pygmentize_command):
        source_md5 = self.sourcecode_md5(code_to_pygmentize, pygmentize_command)
        absolute_path = CACHE_DIR + source_md5
        if (os.path.exists(absolute_path)):
            pygmentized_code_file = open(absolute_path, 'r')
            code = pygmentized_code_file.read()
            pygmentized_code_file.close()
            return code
        else:
            return None
    
class PygmentizeExecutor():
    def __init__(self, cache_manipulator):
        self.cache_manipulator = cache_manipulator
        
    def fork_pygmentize_stdin(self):
        exit_val = 0
        try:
            exit_val = load_entry_point('pygments-hack==0.2', 'console_scripts', 'pygmentize')()                                                                                                                         
        except Exception:
            exit_val = load_entry_point('Pygments', 'console_scripts', 'pygmentize')()                                                                                                                         
        sys.exit(exit_val)
        
    def fork_pygmentize_to_file(self, code_to_pygmentize, pygmentize_command, output_filename):
        md5 = self.cache_manipulator.sourcecode_md5(code_to_pygmentize, pygmentize_command)
        exit_val = 0
        try:
            exit_val = load_entry_point('pygments-hack==0.2', 'console_scripts', 'pygmentize')()                                                                                                                         
        except Exception:
            exit_val = load_entry_point('Pygments', 'console_scripts', 'pygmentize')()
        absolute_path = CACHE_DIR + md5
        shutil.copy2(output_filename, absolute_path)
        sys.exit(exit_val)
    
class PygmentizeCache():
    def __init__(self, argv, executor, cache_manipulator):
        self.pygmentize_arguments = argv
        self.pygmentize_command = self.parse_pygmentizeargs()
        self.pygmentize_executor = executor
        self.cache_manipulator = cache_manipulator

    def contains_input_file(self):
        contains =  not self.pygmentize_arguments[len(self.pygmentize_arguments) - 2].startswith("-")
        return contains

    def read_code(self, args):
        f = open(args[len(args) - 1], 'r')
        code = f.read()
        f.close()
        return code
        
    def parse_pygmentizeargs(self):
        pygmentize_cmd = "pygmentize"
        for c in self.pygmentize_arguments:
            if c == self.pygmentize_arguments[0]:
                continue
            c = c.replace(" ", "")
            pygmentize_cmd += " " + c
        return pygmentize_cmd
        
    def write_to_cache(self, source_md5, pygmentized_code):
        absolute_path = CACHE_DIR + source_md5
        pygmentized_code_file = open(absolute_path, 'w')
        pygmentized_code_file.write(pygmentized_code)
        pygmentized_code_file.close()

    def find_output_filename(self):
        for i in range(len(self.pygmentize_arguments)):
            if (self.pygmentize_arguments[i] == "-o"):
                return self.pygmentize_arguments[i + 1]
        return None
    
    def fork_pygmentize_stdin(self):
        self.pygmentize_executor.fork_pygmentize_stdin()
        
    def fork_pygmentize_to_file(self, code_to_pygmentize, output_filename):
        self.pygmentize_executor.fork_pygmentize_to_file(code_to_pygmentize, self.pygmentize_command, output_filename)
    
    def find_from_cache_or_fork(self):
        code_to_pygmentize = self.read_code(self.pygmentize_arguments)
        pygmentized_code = self.cache_manipulator.find(code_to_pygmentize, self.pygmentize_command)
        output_filename = self.find_output_filename()
        if pygmentized_code != None:
            log("lendo do cache")
            output_file = open(output_filename, "w")
            output_file.write(pygmentized_code)
            output_file.close()
        else: 
            self.fork_pygmentize_to_file(code_to_pygmentize, output_filename)
        
    def execute(self):
        if not self.contains_input_file():
            self.fork_pygmentize_stdin()
        else:
            self.find_from_cache_or_fork()