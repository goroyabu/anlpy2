#!/usr/local/bin/python3

import enum

class AnalysisStatus(enum.IntEnum) :
    OKEvent   = enum.auto()
    SkipEvent = enum.auto()
    QuitLoop  = enum.auto()

    OKFunc = enum.auto()
    ErrFunc = enum.auto()
