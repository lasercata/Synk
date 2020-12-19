#!/bin/python3
# -*- coding: utf-8 -*-

'''This script is useful to check differencies and sync trees.'''

auth = 'Lasercata'
last_update = '2020.12.18'
version = '0.1'


##-import
#------main
from os import walk, listdir, path, stat
#from os.path import abspath, exists

import hashlib

#------For color
import ctypes
import platform

#------For parser
import argparse

##-Useful
#---------Color
class Color:
    '''Class dealing with the console coloring'''

    #------constants
    c_prog = 'white'
    c_succes = 'green'
    c_err = 'red'
    c_warn = 'orange'
    c_title = 'white'

    c_dir = 'light_blue'
    c_file = 'blue'


    #------init
    def __init__(self, color, use=True):
        '''
        Initiate Color class.

        - color : the color to use ;
        - use : a bool which indicates if use the color.
        '''

        if platform.system() == 'Windows':
            handle = ctypes.windll.kernel32.GetStdHandle(-11)

            self.col = lambda x : ctypes.windll.kernel32.SetConsoleTextAttribute(handle, x)

            self.dct_col = {'invisible' : 0, 'orange' : 1, 'blue' : 9, 'green' : 10, 'light_blue' : 11,
            'red' : 12, 'pink' : 13, 'yellow' : 14, 'white' : 15}


        elif platform.system() == 'Linux':
            self.col = lambda x : print('\033[' + str(x) + 'm', end='')

            self.dct_col = {'none' : 0, 'bold' : 1, 'lite' : 2, 'italics' : 3, 'underline' : 4,
            'flaches' : 5, 'norm' : 6, 'reverse' : 7, 'invisible' : 8, 'cross' : 9,

            'black' : 30, 'red' : 31, 'green' : 32, 'orange' : 33, 'light_blue' : 34,
            'pink' : 35, 'blue' : 36, 'white' : 37}

        if not use:
            self.col = lambda x: None

        self.use = use

        self.color = color


    def set(self):
        '''Changes the color'''

        try:
            self.col(self.dct_col[self.color])

        except KeyError:
            raise ValueError('The input was not recognized !!!')


    def out(self, prompt, color_2=c_prog, sp=False):
        '''Print prompt in the self.color color.'''

        self.set()
        if sp:
            print('')

        print(prompt)
        Color(color_2).set()


    def bold_out(self, prompt, color2=c_prog, sp=False):
        '''Same as self.out, but in bold, if possible.'''

        if platform.system() == 'Linux':
            Color('bold', self.use).set()

        self.out(prompt, color2, sp)

        if platform.system() == 'Linux':
            Color('none', self.use).set()


#---------list files
def listf(path_='.'):
    '''Lists the files (and not the directories) at the path.'''

    l = []
    f_path = path.abspath(path_)

    for f in listdir(f_path):
        if path.isfile(f_path + '/' + f):
            l.append(f)

    return l


#---------list differencies
def list_dif(l1, l2):
    '''
    Return three lists :
        - l1_ : contain the elements that are only in l1 ;
        - l2_ : contain the elements that are only in l2 ;
        - lc : contain the elements that are in both lists.
    '''

    l1_ = []
    l2_ = []
    lc = []

    for k in l1:
        if k not in l2:
            l1_.append(k)

    for k in l2:
        if k not in l1:
            l2_.append(k)

    for k in l1:
        if k not in l1_:
            lc.append(k)

    return l1_, l2_, lc


#---------hash file
def file_hash(fn, buffer_size=2**16, h=hashlib.sha256()):
    '''
    Return the hash of a file.

    - fn : the file's name ;
    - buffer_size : the buffer size ;
    - h : the hash to use. Should be of the form 'hashlib.{hashtype}()'.
    '''

    with open(fn, 'rb') as f:
        b = f.read(buffer_size)

        while len(b) > 0:
            h.update(b)
            b = f.read(buffer_size)

    return h.hexdigest()



##-main
class Synk:
    '''Class which compare and sync trees'''

    def __init__(self, path_1, path_2, color_use=True):
        '''Init class.'''

        self.path_1 = path_1
        self.path_2 = path_2

        self.f_path_1 = path.abspath(path_1)
        self.f_path_2 = path.abspath(path_2)

        if not path.exists(self.f_path_1):
            raise ValueError("path1 don't exists !")

        if not path.exists(self.f_path_2):
            raise ValueError("path2 don't exists !")

        self.color_use = color_use


    def compare(self, exclude, ret_type='h'):
        '''
        Use the self._compare method.

        - exclude : list of the patterns to exclude.
        - ret_type : 'h' (human readable) or 'n' (normal) : the way how the string are formed for the return.
        '''

        if ret_type not in ('h', 'human', 'n', 'normal'):
            raise ValueError(f'The argument "ret_type" should be set to "h" or "n", however "{ret_type}" was found !!!')

        m_dirs, m_files, updt_f = self._compare(exclude, ret_type)
        m_dirs[1] += Synk(self.path_2, self.path_1)._compare(exclude, ret_type)[0][2]

        return m_dirs, m_files, updt_f


    def _compare(self, exclude, ret_type='h'):
        '''Compare the trees from two points.'''

        m_dirs = {1: [], 2: []}     # Missing directories
        m_files = {1: [], 2: []}    # Missing files
        updt_f = {1: [], 2: []}     # Updated files : first list contain outdated files in path_1

        for r, d, f in walk(self.f_path_1):
            relative = r[len(self.f_path_1):] # Relative path from the path 1 or 2.

            if not path.exists(self.f_path_2 + relative): #Check if the same path exists in path_2/
                if ret_type == 'n':
                    m_dirs[2].append(f'.{relative}')
                else:
                    m_dirs[2].append('{} (in .{})'.format(relative.split('/')[-1], '/'.join(relative.split('/')[:-1])))

            else: #If it exists, check the files
                f1, f2, fc = list_dif(f, listf(self.f_path_2 + relative))

                for k in f1:
                    if True not in [j in k for j in exclude]: #Pythonic way to check if {k} don't contain an extention of exclude.
                        if ret_type == 'n':
                            m_files[2].append(f'.{relative}/{k}')
                        else:
                            m_files[2].append(f'{k} (in .{relative})')

                for k in f2:
                    if True not in [j in k for j in exclude]:
                        if ret_type == 'n':
                            m_files[1].append(f'.{relative}/{k}')
                        else:
                            m_files[1].append(f'{k} (in .{relative})')

                for file in fc: #Check date
                    fc_1 = '{}{}/{}'.format(self.f_path_1, relative, file)
                    fc_2 = '{}{}/{}'.format(self.f_path_2, relative, file)

                    if (file_hash(fc_1) != file_hash(fc_2)) and (True not in [j in file for j in exclude]):
                        if round(path.getmtime(fc_1), -2) < round(path.getmtime(fc_2), -2):
                            if ret_type == 'n':
                                updt_f[1].append(f'.{relative}/{file}')
                            else:
                                updt_f[1].append(f'{file} (in .{relative})')

                        elif round(path.getmtime(fc_1), -2) > round(path.getmtime(fc_2), -2):
                            if ret_type == 'n':
                                updt_f[2].append(f'.{relative}/{file}')
                            else:
                                updt_f[2].append(f'{file} (in .{relative})')

                #todo: also compare file size (difference of size) if mdate is different


        return m_dirs, m_files, updt_f


    def gcompare(self, exclude, ret_type):
        '''Print the result of self.compare in a colorful human readable format.'''

        print('\nProcessing ...\n')

        m_dirs, m_files, updt_f = self.compare(exclude, ret_type)
        n = 0

        if not(m_dirs[1] == m_files[1] == []):
            Color(Color.c_title).bold_out(f"Missing in '{self.path_1}' :")

            for d in m_dirs[1]:
                Color(Color.c_dir, self.color_use).bold_out(f'\t{d}')

            for fl in m_files[1]:
                Color(Color.c_file, self.color_use).out(f'\t{fl}')

            print('')
            n += 1

        if len(updt_f[1]) != 0:
            Color(Color.c_title).bold_out(f"Outdated files in '{self.path_1}' :")

            for fl in updt_f[1]:
                Color(Color.c_file, self.color_use).out(f'\t{fl}')

            print('')
            n += 1


        if not(m_dirs[2] == m_files[2] == []):
            Color(Color.c_title).bold_out(f"Missing in '{self.path_2}' :")

            for d in m_dirs[2]:
                Color(Color.c_dir, self.color_use).bold_out(f'\t{d}')

            for fl in m_files[2]:
                Color(Color.c_file, self.color_use).out(f'\t{fl}')

            print('')
            n += 1

        if len(updt_f[2]) != 0:
            Color(Color.c_title).bold_out(f"Outdated files in '{self.path_2}' :")

            for fl in updt_f[2]:
                Color(Color.c_file, self.color_use).out(f'\t{fl}')

            print('')
            n += 1


        if n == 0:
            Color(Color.c_succes, self.color_use).out('Trees are up to date !\n')


    def sync(self):
        '''Use self.compare to synchronise the two paths.'''

        m_dirs, m_files, updt_f = self.compare('n')



##-Using interface
class Parser:
    '''Class which allow to use Synk in console parser mode.'''

    def __init__(self):
        '''Initiate Parser'''

        self.parser = argparse.ArgumentParser(
            prog='Synk',
            description='List differencies between path1 and path2.\nCan sync the two trees.',
            epilog='Examples :\n\tSynk path1 path2\n\tSynk -s path1 path2',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        self.parser.add_argument(
            'path1',
            help='Path to the first folder to synchronise'
        )
        self.parser.add_argument(
            'path2',
            help='Path to the second folder to synchronise'
        )

        self.parser.add_argument(
            '-s', '--sync',
            help='Synchronise the two trees to the last version (not implemented)',
            action='store_true'
        )

        self.parser.add_argument(
            '-x', '--exclude',
            help='Patterns to exclude. "," (comma) between them.'
        )

        self.parser.add_argument(
            '-f', '--format',
            help='Format of the printed paths. "h" for human readable, "n" for normal output. Default is "h".',
            choices=('h', 'human', 'n', 'normal')
        )

        self.parser.add_argument(
            '-c', '--color',
            help='Use color or not. 0 : no color ; 1 : use color. Default is 1.',
            choices=(0, 1),
            type=int
        )


    def parse(self):
        '''Parse the args'''

        #------Check arguments
        args = self.parser.parse_args()

        #---exclude
        if args.exclude != None:
            exclude = args.exclude.split(',')

        else:
            exclude = []

        #---format
        if args.format == None:
            ret_type = 'h'

        else:
            ret_type = args.format

        #---color
        if args.color != None:
            color_use = args.color

        else:
            color_use = True

        #---paths
        if not path.exists(args.path1):
            Color(Color.c_err, color_use).out(f"Synk: cannot access '{args.path1}' : No such file or directory")
            return -1

        if not path.exists(args.path2):
            Color(Color.c_err, color_use).out(f"Synk: cannot access '{args.path2}' : No such file or directory")
            return -1

        if args.path1 == args.path2:
            Color(Color.c_warn, color_use).out('You selected the same path two times !\nContinuing anyway ...')

        #------Sync
        synker = Synk(args.path1, args.path2, color_use)

        if args.sync:
            print('Todo.')

        else:
            synker.gcompare(exclude, ret_type)




##-run
if __name__ == '__main__':
    #Color(Color.c_prog).set()

    app = Parser()
    app.parse()

