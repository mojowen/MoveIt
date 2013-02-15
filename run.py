#!/usr/local/bin/python

import imp
import sys
import inspect
import os
import commands

script_to_run = sys.argv.pop(1).replace('.py','') # removes the first argument so you can use the arguemnts in a script without worrying about it

print '/scripts/'+script_to_run+'.py'

directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

os.chdir( directory )

imp.load_source(script_to_run, 'scripts/'+script_to_run+'.py')