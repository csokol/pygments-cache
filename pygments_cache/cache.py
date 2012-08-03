#!/usr/bin/python

import sys, hashlib, os, shlex, time, shutil, traceback, redis
from MySQLdb import *
from pkg_resources import load_entry_point

CACHE_DIR = os.getenv("HOME") + "/.pygments/cache/"

def log(string):
    log = open('/tmp/pygmentize-output', 'a')
    log.write(string + "\n")
    log.close

class CacheManipulator():
    def __init__(self):
        self.connection = connect(host="localhost", user="root", db="pygments")
        self.cached_code = ""
        self.pool = redis.ConnectionPool(host='localhost', port=6379, db=1)
        self.redis_connection = redis.Redis(connection_pool=self.pool)
        #redis.StrictRedis(host='localhost', port=6379, db=1)
        
    def sourcecode_md5(self, sourcecode, pygmentize_cmd):
        md5 = hashlib.md5()
        md5.update(sourcecode + pygmentize_cmd)
        return md5.hexdigest()
        
    def find_and_copy(self, code_to_pygmentize, pygmentize_command, output_filename):
        source_md5 = self.sourcecode_md5(code_to_pygmentize, pygmentize_command)
        absolute_path = CACHE_DIR + source_md5
        if (self.find_from_db(source_md5)):
            shutil.copy2(absolute_path, output_filename)
            out_file = open(output_filename, "w")
            out_file.write(self.cached_code)
            return True
        else:
            return None
            
    def find_from_db(self, md5):
        code = self.redis_connection.get(md5)
        if code != None:
            self.cached_code = code
            return True
        return False
        
    def write(self, code_to_pygmentize, pygmentize_command, output_filename):
        md5 = self.sourcecode_md5(code_to_pygmentize, pygmentize_command)
        absolute_path = CACHE_DIR + md5
        self.save_to_db(md5, output_filename)
        #shutil.copy2(output_filename, absolute_path)
        
    def save_to_db(self, md5, output_filename):
        code = open(output_filename, "r").read()
        self.redis_connection.set(md5, code)
    
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
        exit_val = 0
        try:
            exit_val = load_entry_point('pygments-hack==0.2', 'console_scripts', 'pygmentize')()                                                                                                                         
        except Exception:
            exit_val = load_entry_point('Pygments', 'console_scripts', 'pygmentize')()
        self.cache_manipulator.write(code_to_pygmentize, pygmentize_command, output_filename)
        sys.exit(exit_val)
    
class PygmentizeCache():
    def __init__(self, argv, executor, cache_manipulator):
        self.pygmentize_arguments = argv
        self.pygmentize_command = self.parse_pygmentizeargs()
        self.pygmentize_executor = executor
        self.cache_manipulator = cache_manipulator
        self.create_cache_dir()
        
    def create_cache_dir(self):
        if not os.path.isdir(CACHE_DIR):
            os.makedirs(CACHE_DIR)

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
        output_filename = self.find_output_filename()
        code_to_pygmentize = self.read_code(self.pygmentize_arguments)
        found_and_copied = self.cache_manipulator.find_and_copy(code_to_pygmentize, self.pygmentize_command, output_filename)
        if found_and_copied:
            log("lendo do cache")
        else: 
            self.fork_pygmentize_to_file(code_to_pygmentize, output_filename)
        
    def execute(self):
        if not self.contains_input_file():
            self.fork_pygmentize_stdin()
        else:
            self.find_from_cache_or_fork()