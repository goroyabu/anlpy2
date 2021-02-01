#!/usr/bin/env python3

import os, time, datetime, argparse
import enum, math
import numpy, scipy, ROOT
import builtins

from .analysis_status import AnalysisStatus as stt
from .event_flags import EventFlags as evs

class VANLModule :
    """Basic class of analysis module

    This class has 5 user-defined functions :

        1. __init__             : constructor of class
        2. user_output_basename : define output file name
        3. user_before_loop     : called once before loop
        4. user_event_routine   : called for each event in loop
        5. user_after_loop      : called once after loop

    Attributes:
        self.input_file_name (str):
        self.input_file (ROOT.TFile):
        self.input_tree_name (str):
        self.input_tree (ROOT.TTree):
        self.output_file_name (str):
        self.output_file (ROOT.TFile):
    """

    def __init__(self,input_file_name,args,intree,outdir='.',nentries=-1,printfreq=100,verbose=0) :
        """
        Args :
            input_file_name (str): a name of ROOT file to open
            args (argparse.Namespace) : a return value of argparse.ArgumentParser.parse_args()
            intree (str): a name of tree (ROOT.TTree) to load
            outdir (str): a name of directory to output a new file
            nentries (int): number of entries to read in loop
            printfreq (int): frequency (number of entries) to print progress
            verbose (int): verbose level to print message


        Examples : This method must be called in constructor of user-defined class like this.

            class UserModule(VANLModule) :

                def __init__(self,input_file_name,args):

                    ### CALL AT FIRST ###
                    super().__init__( input_file_name, args )
                    #####################
        """

        self.args = args

        self.input_file_name = input_file_name
        # self.input_file = self.open_root( self.input_file_name )
        #
        self.input_tree_name  = intree
        # self.input_tree = self.load_tree( self.input_tree_name )
        #
        outbase = outdir + '/' + self.user_output_basename( self.input_file_name )
        self.output_file_name = outbase + '.root'
        #
        # self.output_file = self.create_root( self.output_file_name )
        #
        # self.nentries = self.input_tree.GetEntries()
        # if 0 < nentries and nentries < self.nentries :
        #     self.nentries = nentries
        #
        self.nentries = nentries
        self.print_frequency = printfreq
        self.verbose = verbose
        #
        self.start_time = datetime.datetime.now()
        self.prev_time = datetime.datetime.now()

    def _open_root(self,file_name) :

        file = ROOT.TFile( file_name )
        if file == None or file.IsZombie() == True :
            print( '***Error*** : Opening', file_name, 'is failed' )
            return None

        print( ' Open File :', file_name )
        return file

    def _load_tree(self,tree_name) :

        if self.input_file == None :
            return None

        tree = self.input_file.Get( tree_name )
        if tree == None :
            print( '***Error*** :', tree_name, 'is not found in', self.input_file_name )
            return None

        print( ' Load Tree :', tree_name, 'from', self.input_file_name )

        nentries = tree.GetEntries()
        if self.nentries < 0 or nentries < self.nentries :
            self.nentries = nentries

        return tree

    def _create_root(self,file_name) :

        if self.input_file == None :
            return None

        if file_name == self.input_file_name :
            print( '***Error*** : Attempting to create opened file ', self.input_file_name )
            return None

        file = ROOT.TFile( file_name, 'recreate' )
        if file == None or file.IsZombie() == True :
            print( '***Error*** : Creating', file_name, 'is failed' )
            return None

        print( ' New  File :', file_name )
        return file

    def open_files(self) :
        """Method to open and create ROOT files.

        This method set pointers of TFile and TTree to attributes of this class.
        This method is recommended to be called in ``user_before_loop``.

        Returns :
            AnalysisStatus: `error_before_loop` if error occurred, `ok_before_loop` otherwise.
        """

        self.input_file = self._open_root( self.input_file_name )
        if self.input_file is None :
            return self.error_before_loop()

        self.input_tree = self._load_tree( self.input_tree_name )
        if self.input_tree is None :
            return self.error_before_loop()

        self.output_file = self._create_root( self.output_file_name )
        if self.output_file is None :
            return self.error_before_loop()

        return self.ok_before_loop()

    def _print_progress(self,current_entry) :

        current_entry = int(current_entry)

        if current_entry == 0 :
            self.start_time = datetime.datetime.now()

        if current_entry%self.print_frequency == 0 :

            now = datetime.datetime.now()
            dt = (now-self.start_time).total_seconds()
            rest_entries = self.nentries - current_entry
            progress_in_dt = current_entry/dt
            rest_time = 0
            if progress_in_dt != 0 :
                rest_time = rest_entries/progress_in_dt

            h = rest_time//3600
            rest_time = rest_time%3600
            m = rest_time//60
            rest_time = rest_time%60
            s = rest_time

            self.prev_time = now
            rest=f': Time {h:02.0f}:{m:02.0f}:{s:04.1f}'

            print(
                '\r', '{:9d}/{:9d}({:5.2f}%)'\
                .format( current_entry, self.nentries,\
                float( current_entry/self.nentries*100.0 ) ),
                rest, end=''
                )

        if current_entry == self.nentries - 1 :
            print( '' )

        return current_entry

    def run_analysis(self) :
        """Method to execute analysis loop.

        Note : Analysis flow has 3 steps,
            1. call user_before_loop
            2. loop with calling user_event_routine N-times
            3. call user_after_loop
        """

        if self.user_before_loop() != stt.OKFunc :
            return stt.ErrFunc

        entry_list = range( self.nentries )
        entries = numpy.array( [ range( self.nentries ) ] )

        # numpy.apply_along_axis( self.run_loop, axis=0, arr=entries )
        for entry in entry_list :
            evs.clear()
            if self._run_loop(entry) == stt.QuitLoop :
                break

        if self.user_after_loop() != stt.OKFunc :
            return stt.ErrFunc

        evs.output()

    def _run_loop(self,current_entry) :

        current_entry = self._print_progress( current_entry )
        self.input_tree.GetEntry( current_entry )
        return self.user_event_routine(current_entry)

    def _print_error(self,where,message=None) :
        if message is None :
            print( f'*** Error in {where} ***' )
        else :
            print( f'*** Error in {where} *** : {message}' )

    def ok_event(self) :
        """
        Note :
            Call in ``user_event_routine`` method
        """
        evs.accumulate()
        return stt.OKEvent

    def skip_event(self) :
        """
        Note :
            Call in ``user_event_routine`` method
        """
        evs.accumulate()
        return stt.SkipEvent

    def quit_loop(self) :
        """
        Note :
            Call in ``user_event_routine`` method
        """
        evs.accumulate()
        self._print_progress( self.nentries-1 )
        return stt.QuitLoop

    def ok_before_loop(self) :
        """
        Note :
            Call in ``user_before_loop`` method
        """
        return stt.OKFunc

    def error_before_loop(self) :
        """
        Note :
            Call in ``user_before_loop`` method
        """
        return stt.ErrFunc

    def ok_after_loop(self) :
        """
        Note :
            Call in ``user_after_loop`` method
        """
        return stt.OKFunc

    def error_after_loop(self) :
        """
        Note :
            Call in ``user_after_loop`` method
        """
        return stt.ErrFunc

    def user_output_basename(self,file_name) :
        """Method to determine name of output file using that of input file.

        Note :
            returns of this method has no extension (such as .root) and directory path

        Args :
            file_name (str): input file name

        Returns :
            str: basename of output file without extension
        """
        base = os.path.basename( file_name )
        name, ext = os.path.splitext( base )
        return name+'_out'

    def user_event_routine(self,current_entry) :
        """Method called each entry in loop.

        Note :
            When this method is called,
            the function of input tree, TTree::GetEntry(current_entry), is already called.

        Args :
            current_entry (int): ID of current entry. The first entry corresponds to 0.

        Returns :
            AnalysisStatus:

            Return by using methods of this class for each cases

                1. To end this event normally, return self.ok_event()
                2. To end this event and go to the next, return self.skip_event()
                3. To end this event and exit from the loop, return self.quit_loop()
        """

        return self.ok_event()

    def user_before_loop(self) :
        """Method called once before loop. Histograms are defined here.

        Note :
            To Open a input file and create a new file, call `open_files` method here.

        Returns :
            AnalysisStatus:

            Return by using methods of this class for each cases

                1. To begin loop, return self.ok_before_loop()
                2. To end the program without entering loop due to error, return self.error_before_loop()
        """

        if self.open_files() is self.error_before_loop() :
            return self.error_before_loop()

        return self.ok_before_loop()

    def user_after_loop(self) :
        """Method called once after loop. Histograms are saved in files here.

        Returns :
            AnalysisStatus: To end this method, return self.ok_after_loop.
        """

        return self.ok_after_loop()
