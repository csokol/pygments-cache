#!/usr/bin/python

import sys, hashlib, os, shlex, time, shutil, traceback
from subprocess import Popen, PIPE, STDOUT

CACHE_DIR = os.getenv("HOME") + "/.pygments/cache/"

def log(string):
    log = open('/tmp/pygmentize-output', 'a')
    log.write(string + "\n")
    log.close
    
class PygmentizeExecutor():
    def fork_pygmentize_stdin(self, pygmentize_cmd):
        p = Popen(pygmentize_cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        stdin_input = sys.stdin.read()
        p.stdin.write(stdin_input)
        p.stdin.close()
        return p.stdout.read()
        
    def fork_pygmentize_to_file(self, pygmentize_cmd, md5, output_filename):
        p = Popen(pygmentize_cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        p.communicate(input=None)
        absolute_path = CACHE_DIR + md5
        shutil.copy2(output_filename, absolute_path)
    
class PygmentizeCache():
    def __init__(self, argv, executor):
        self.pygmentize_arguments = argv
        self.pygmentize_command = self.parse_pygmentizeargs()
        self.pygmentize_executor = executor

    def contains_input_file(self, args):
        contains =  not args[len(args) - 2].startswith("-")
        return contains

    def read_code(self, args):
        f = open(args[len(args) - 1], 'r')
        code = f.read()
        f.close()
        return code
        
    def parse_pygmentizeargs(self):
        pygmentize_cmd = "pygmentize-orig"
        for c in self.pygmentize_arguments:
            if c == self.pygmentize_arguments[0]:
                continue
            c = c.replace(" ", "")
            pygmentize_cmd += " " + c
        return pygmentize_cmd
        
    def sourcecode_md5(self, sourcecode, pygmentize_cmd):
        md5 = hashlib.md5()
        md5.update(sourcecode + pygmentize_cmd)
        return md5.hexdigest()
        
    def find_from_cache(self, source_md5):
        absolute_path = CACHE_DIR + source_md5
        if (os.path.exists(absolute_path)):
            pygmentized_code_file = open(absolute_path, 'r')
            code = pygmentized_code_file.read()
            pygmentized_code_file.close()
            return code
        else:
            return None
            
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
        self.pygmentize_executor.fork_pygmentize_stdin(self.pygmentize_command)
        
    def fork_pygmentize_to_file(self, md5, output_filename):
        self.pygmentize_executor.fork_pygmentize_to_file(self.pygmentize_command, md5, output_filename)
    
    def find_from_cache_or_fork(self):
        code_to_pygmentize = self.read_code(self.pygmentize_arguments)
        md5 = self.sourcecode_md5(code_to_pygmentize, self.pygmentize_command)
        pygmentized_code = self.find_from_cache(md5)
        output_filename = self.find_output_filename()
        if pygmentized_code != None:
            log("lendo do cache")
            output_file = open(output_filename, "w")
            output_file.write(pygmentized_code)
            output_file.close()
        else: 
            self.fork_pygmentize_to_file(md5, output_filename)
        
    def execute(self):
        if not self.contains_input_file(sys.argv):
            output = self.fork_pygmentize_stdin()
            print output
        else:
            self.find_from_cache_or_fork()