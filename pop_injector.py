#!/usr/bin/env python

import subprocess as sp
from optparse import OptionParser
import sys
import re
import time
import os

import gdbmi


'''
this script implement an injector using gdb
'''
def move(normal, src, dst, var, folder):
    # check whether the restart destination folder exist
    while not os.path.exists(dst):
        print 'creating: ', dst
        os.system('mkdir '+ dst) 
       
    #create the folder to store data with fault injected
    var = var.strip(' ')
    dirname = os.path.join(dst, var)

    print 'checking: ', dirname
    while not os.path.exists(dirname):
        print 'creating: ', dirname
        os.system('mkdir '+ dirname)

    fault_dir = os.path.join(dirname, str(folder))
    
    while not os.path.exists(fault_dir):
        print 'creating: ', fault_dir
        os.system('mkdir '+ fault_dir)
       
    cmd  = ' '.join(['mv', src+'/*', fault_dir])
    os.system(cmd)    


    dst = os.path.join(dirname, '0')

    while not os.path.exists(dst):
        cmd = ' '.join(['ln -s', normal, dst])
        os.system(cmd);
    ''' end of moving data '''


if __name__ == "__main__":
    usage = "usage: %prog fault-file, exec, args for exec"
    prefix = '/tmp/cchen/pop/'
    r_src  = os.path.join(prefix, 'restart')
    d_src  = os.path.join(prefix, 'diag')
    t_src  = os.path.join(prefix, 'tavg')

    prefix = '/tmp/cchen/POP'
    r_dst  = os.path.join(prefix, 'restart')
    d_dst  = os.path.join(prefix, 'diag')
    t_dst  = os.path.join(prefix, 'tavg')

    r_normal = '/tmp/cchen/POP/normal/restart/'
    d_normal = '/tmp/cchen/POP/normal/diag/'
    t_normal = '/tmp/cchen/POP/normal/tavg/'

    parser = OptionParser(usage=usage)
    (opts, args) = parser.parse_args()
    if len(args) == 0:
        parser.print_help();
        sys.exit(-1);

    faults_file = args[0];
    target = args[1];
    exec_args = args[2:];
    
    print 'exec:', target
    print 'exec args:', exec_args
    print 'faults:', faults_file

    faults = gdbmi.read_file(faults_file);
    print 'number of faults: ', len(faults)
    for i in faults:
        print i
    print '\n\n'

    folder = 0
    currvar = ''
    for fault in faults:
        print 'inject the fault:', fault

        step_var = fault['step']['name']
        step = fault['step']['val']
        var = fault['mem']
        fault_val = fault['fault']
        s = gdbmi.Session(target = target, args = exec_args,\
                        language = 'fortran')
        s.start()
        s.watch_insert(step_var, step)
        s.exec_continue()
        s.inject(var, fault_val)
        s.exec_continue()
        s.finish() 
        
        '''
        move data to a center
        '''
        # formate the var to use it for folder name
        var = var.replace('::', '.')
        var = var[:var.find('(')]
        if currvar != var:
            currvar = var
            folder = 1
        
        
        #move(r_normal, r_src, r_dst, var, folder)
        move(d_normal, d_src, d_dst, var, folder)
        move(t_normal, t_src, t_dst, var, folder)

        folder = folder+1
        time.sleep(2)
        print '\n\n'

