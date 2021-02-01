#!/usr/bin/env python3

# from analysis_framework import analysis_status as stt
from .analysis_status import AnalysisStatus as stt

class EventFlags :
    """Class to set various flags for each event.

    Please see description of `when` method for detaild usage.

    Examples (recommended) :
        Standard usage using with `when` method.

        >>> energy
        200.0
        >>> EventFlags.when( energy <= 511.0, set_flag='under511', otherwise_set_flag='over511' )
        >>> EventFlags.accumulate() # automatically called at the end of analysis by module class
        >>> EventFlags.output()     # the same as above

        ::

             *** results of Event selection *** < Number of selects :     2 >
                     1 :  under511
                     0 :  over511

    Examples :
        >>> EventFlags.define( 'some_selection' )
        >>> EventFlags.define( 'other_selction' )
        >>> EventFlags.set( 'some_selection' ) # if `some_selection` is True
        >>> EventFlags.accumulate()            # called in each event
        >>> EventFlags.output()                # called at the end of analysis

        ::

             *** results of Event selection *** < Number of selects :     2 >
                     1 :  some_selection
                     0 :  other_selction
    """

    __dict_of_flags = {}
    __verbose_level = 1
    __status        = stt.OKEvent

    @classmethod
    def ndef(cls) :
        """
        Returns :
            int: Number of defined flags
        """
        return len( EventFlags.__dict_of_flags )

    @classmethod
    def status(cls) :
        """
        Returns :
            AnalysisStatus: Status of EventFlags
        """
        return __status

    @classmethod
    def has(cls,key) :
        """
        Args :
            key (str): name of a flag

        Returns :
            bool: True if flag is defined, False otherwise.
        """
        if key in EventFlags.__dict_of_flags :
            return True
        return False

    @classmethod
    def __newkey(cls,key) :

        iter = 2
        while True :
            candidate = key+'-{:d}'.format( iter )
            if EventFlags.has( candidate ) == False :
                break
            iter += 1

        return candidate

    def __init__(self,key) :

        if EventFlags.has( key ) :
            self.__key = EventFlags.__newkey( key )
        else :
            self.__key = key

        self.__count = 0.0
        self.__isset = False
        self.__accum = 0.0
        # EventFlags.__dict_of_flags[ self.__key ] = self

    @classmethod
    def define(cls,key) :
        """
        Args :
            key (str): name of a flag
        """

        if EventFlags.has( key ) == True :
            return
        temp = EventFlags( key )
        EventFlags.__dict_of_flags[ temp.__key ] = temp

    @classmethod
    def set(cls,key,val=1.0) :
        """Method to set a flag

        Args :
            key (str): name of a flag
            val (float): value of a flag (default:1)

        Note :
            If the flag is already set in the event, the value is overwritten.
        """
        if EventFlags.has( key ) == False :
            # EventFlags.define( key )
            return False
        EventFlags.__dict_of_flags[ key ].__count = val
        EventFlags.__dict_of_flags[ key ].__isset = True

    @classmethod
    def add(cls,key,val=1.0) :
        """Method to add a value to flag

        Args :
            key (str): name of a flag
            val (float): value of a flag (default:1)

        Note :
            If the flag is already set in the event, the sum of current and new value is set.
        """
        if EventFlags.has( key ) == False :
            return False
        EventFlags.__dict_of_flags[ key ].__count += val
        EventFlags.__dict_of_flags[ key ].__isset = True

    @classmethod
    def is_set(cls,key) :
        """Method returns which the flag is set

        Args :
            key (str): name of a flag

        Returns :
            True if set in this event, False otherwise.
        """
        if EventFlags.has( key ) == False :
            return False
        return EventFlags.__dict_of_flags[ key ].__isset

    @classmethod
    def any(cls,list_of_keys) :
        """
        Args :
            list_of_keys (list<str>): list of flag names
        """
        return any( EventFlags.is_set( key ) for key in list_of_keys )

    @classmethod
    def all(cls,list_of_keys) :
        """
        Args :
            list_of_keys (list<str>): list of flag names
        """
        return all( EventFlags.is_set( key ) for key in list_of_keys )

    @classmethod
    def get(cls,key) :
        """
        Args :
            key (str): name of a flag

        Returns :
            float: Current value set at this event in a flag
        """
        if EventFlags.has( key ) == False :
            return None
        return EventFlags.__dict_of_flags[ key ].__count

    @classmethod
    def integral(cls,key) :
        """
        Args :
            key (str): name of a flag

        Returns :
            float: Integrated value until this event in a flag
        """
        if EventFlags.has( key ) == False :
            return None
        return EventFlags.__dict_of_flags[ key ].__accum

    @classmethod
    def when(cls,condition=False,set_flag=None,otherwise_set_flag=None) :
        """Method to define and set flags simultaneously. Results are shown at the end of the program.

        Args :
            condition (bool):
            set_flag (str): Flag to set if ``condition`` is True. (default:None)
            otherwise_set_flag (str): Flag to set if ``condition`` is False. (default:None)

        Note :
            Define ``set_flag`` and ``otherwise_set_flag`` if not defined, whether or not ``condition`` is True.

        Examples :

            1. nhits == 0 : Set the flag named 'No_Hit' and skip this event.
            2. nhits != 0 : Set the flag named 'Hit_Exist' and go on the analysis of this event.

            >>> if when( nhits == 0, set_flag='No_Hit', otherwise_set_flag='Hit_Exist' ) :
                    return self.skip_event()

        Returns :
            bool: Returns ``condition``
        """

        if set_flag != None and EventFlags.has( set_flag ) == False :
            EventFlags.define( set_flag )
        if otherwise_set_flag != None and EventFlags.has( otherwise_set_flag ) == False :
            EventFlags.define( otherwise_set_flag )

        if condition == True :
            EventFlags.set( set_flag )
        else :
            EventFlags.set( otherwise_set_flag )

        return condition

    @classmethod
    def accumulate(cls) :
        """
        Note :
            Automatically called at the end of analysis
        """
        for flag in EventFlags.__dict_of_flags.values() :
            flag.__accum += flag.__count
            flag.__count = 0.0
            flag.__isset = False

    @classmethod
    def clear(cls) :
        """Clear values for all flags

        Note :
            Automatically called at the beginning of each event
        """
        for flag in EventFlags.__dict_of_flags.values() :
            flag.__count = 0.0
            flag.__isset = False

    @classmethod
    def reset(cls) :
        """Reset values and integrals for all flags
        """
        for flag in EventFlags.__dict_of_flags.values() :
            flag.__accum = 0.0
            flag.__count = 0.0
            flag.__isset = False

    @classmethod
    def output(cls) :
        """Export results of event selections
        """
        print( '\n *** results of Event selection *** < Number of selects : ',\
            '{:4d}'.format( EventFlags.ndef() ), '>' )
        for flag in EventFlags.__dict_of_flags.values() :
            print( f'{flag.__accum:10.0f} : ', flag.__key )
        print( '' )

if __name__ == '__main__':

    # print(OKEvent,OKEvent.value)
    print(stt.OKEvent,stt.OKEvent.value)
    print(stt.SkipEvent,stt.SkipEvent.value)

    EventFlags.define( 'test' )
    EventFlags.define( 'test' )
    EventFlags.define( 'test2' )
    EventFlags.define( 'otameshi' )

    EventFlags.set( 'test' )

    print( EventFlags.is_set( 'test' ) )
    print( EventFlags.any( [ 'test', 'test2' ] ) )
    print( EventFlags.all( [ 'test', 'test2' ] ) )

    print( EventFlags.has( 'test2' ) )

    EventFlags.accumulate()
    EventFlags.output()
