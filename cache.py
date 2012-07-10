#!/usr/bin/python

import sys, hashlib, os, shlex, time, shutil, traceback
from subprocess import Popen, PIPE, STDOUT

CACHE_DIR = os.getenv("HOME") + "/.pygments/cache/"

def log(string):
    log = open('/tmp/pygmentize-output', 'a')
    log.write(string + "\n")
    log.close
class PygmentizeCache():
    #def __init__(self):

    def contains_input_file(self, args):
        contains =  not args[len(args) - 2].startswith("-")
        return contains

    def read_code(self, args):
        f = open(args[len(args) - 1], 'r')
        code = f.read()
        f.close()
        return code
        
    def parse_pygmentizeargs(self, argv):
        pygmentize_cmd = "pygmentize-orig"
        for c in argv:
            if c == argv[0]:
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
        
    def find_output_filename(self):
        for i in range(len(sys.argv)):
            if (sys.argv[i] == "-o"):
                return sys.argv[i + 1]
        return None
        
    def find_from_cache_or_fork(self, pygmentize_cmd):
        code_to_pygmentize = self.read_code(sys.argv)
        md5 = self.sourcecode_md5(code_to_pygmentize, pygmentize_cmd)
        pygmentized_code = self.find_from_cache(md5)
        output_filename = self.find_output_filename()
        if pygmentized_code != None:
            log("lendo do cache")
            output_file = open(output_filename, "w")
            output_file.write(pygmentized_code)
            output_file.close()
        else: 
            self.fork_pygmentize_to_file(pygmentize_cmd, md5, output_filename)
        