#!/usr/bin/env python3

import os, time, datetime, argparse
import enum, math
import numpy, scipy, ROOT
import builtins

class ArgumentRangeDefaultsHelpFormatter(argparse.HelpFormatter):

    def _get_help_string(self, action):
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:

                    help_min, help_max = '',''

                    if hasattr( action, 'min' ) and hasattr( action, 'max' ) :
                        if action.min != None :
                            help_min = f', min: {action.min}'
                        if action.max != None :
                            help_max = f', max: {action.max}'

                    help += f' (default: %(default)s{help_min}{help_max})'
                    # help += ' (default: %(default)s)'
        return help

class ArrayAction(argparse.Action) :

    def __init__(self, option_strings, dest, nargs=None, default=None, type=None, help=None, metavar=None, sort=False, min=None, max=None, **kwargs):

        if nargs is None or builtins.type(nargs) != int :
            raise ValueError( 'Invalid `nargs`: multiple arguments only allowed' )
        self.array_size = nargs

        if builtins.type(default) is not list :
            raise TypeError( f'Invalid `default`: list of {type.__name__} values is required' )

        if type == None :
            type = builtins.type(default[0])

        default = list( map( type, default ) )

        if min != None and builtins.min(default) < min :
            raise ValueError( f'Invalid `default`: attemp to set value below `min`' )
        if max != None and max < builtins.max(default) :
            raise ValueError( f'Invalid `default`: attemp to set value over `max`' )

        self.min = min
        self.max = max

        type_func = lambda x : list( map( type, x.split(',') ) )
        if sort == True :
            type_func = lambda x : sorted( list( map( type, x.split(',') ) ) )
        super(ArrayAction, self).__init__(option_strings, dest, nargs=1, default=default, type=type_func, help=help, metavar=metavar, **kwargs)

        # print(self.format_usage())

    def __call__(self, parser, namespace, values, option_string=None):

        # print(values)
        values = values[0]
        # print('min', builtins.min(values))
        # print('min', builtins.min(values)<10)

        if self.array_size != None and len(values) != self.array_size :
            parser.error( f'Invalid number of arguments ({values}) for {self.dest} ({self.array_size} is required)' )

        if self.min != None and builtins.min(values) < self.min :
            raise ValueError( f'Invalid arguments : attemp to set value below `min`' )
        if self.max != None and self.max < builtins.max(values) :
            raise ValueError( f'Invalid arguments : attemp to set value over `max`' )

        setattr(namespace, self.dest, values )

    # def format_usage(self) :
    #
    #     print('format_usage')
    #     return 'tameshini'
