# anlpy2

## Installation

For the installation `anlpy2`, the following command is the easiest way.

```sh
 $ git clone https://github.com/goroyabu/anlpy2
 $ pip3 install anlpy2/
```

## Usage

```python

import os, time, datetime, argparse

from ROOT import gROOT, TH1D

from anlpy2.analysis_status import AnalysisStatus as stt
from anlpy2.event_flags import EventFlags as evs
from anlpy2.analysis_framework import VANLModule
from anlpy2.commandline_arguments import ArrayAction as anl_action, ArgumentRangeDefaultsHelpFormatter as anl_formatter

def usage() :

    parser = argparse.ArgumentParser(\
        description='Test program of ANLpy2',\
        formatter_class=anl_formatter,\
        add_help=False,\
        usage='%(prog)s [options] FILE ...' )
    """anlpy2.commandline_arguments.ArgumentRangeDefaultsHelpFormatter

    下記の ArrayAction のパラメータである min, max を help に表示する HelpFormatter
    表示の問題だけなので、他の HelpFormatter でも動作する

    """

    parser.add_argument( 'file', metavar='FILE', type=str, nargs='+', help='file name' )

    parser.add_argument( '--ewindow', metavar='E1,E2', action=anl_action,\
        nargs=2, default=[0,500], help='energy window [keV]', type=float, sort=True, min=0, max=1000 )
    """anlpy2.commandline_arguments.ArrayAction

    カンマ区切りで配列を指定できるオプション引数を作れるアクション
    要素のソートと下限上限が指定可能

    この例でいうと、'--ewindow=0,100' や '--ewindow 0,100' といった使い方になる

    Args :
        nargs (int): 配列サイズ。指定必須。(default:None)
        sort (bool): 要素のソートを行うかどうか。ソートは昇順のみ。(default:False)
        min (float): 下限値。指定されている場合、min 未満の場合はエラーとなる。default では未指定。(default:None)
        max (float): 上限値。基本的に同上。max を超える場合がエラーとなる。(default:None)
    """

    parser.add_argument( '--nentries', metavar='N', type=int, default=-1, help='maximum number of entries to read' )
    parser.add_argument( '--intree', metavar='TREE', type=str, default='g4tree',\
        help='name of input tree' )
    parser.add_argument( '--outdir', metavar='DIRE', type=str, default='.',\
        help='directory name to output' )
    parser.add_argument( '--printfreq', metavar='FREQ', type=int, default=10,\
        help='\nfrequency to print progress' )
    parser.add_argument( '-v', '--verbose', action='count', default=0,\
        help='message verbose level' )

    parser.add_argument( '-h', '--help', action='help',\
        help='show this help message and exit' )

    return parser

class user_analysis(VANLModule) :
    """
    ファイルの開閉、ツリーの読み込み、ループなど解析で基本的な処理を担う

    以下の５つの関数を実装すればよい
    1. __init__             : コンストラクタ
    2. user_output_basename : 出力ファイル名の決定
    3. user_before_loop     : ループ前の処理
    4. user_event_routine   : ループごとに行う処理
    5. user_after_loop      : ループ後の処理

    Parameters:
        self.input_file_name (str): 入力ファイル名
        self.input_file (ROOT.TFile): 入力ファイル
        self.input_tree_name (str): 入力ツリー名
        self.input_tree (ROOT.TTree): 入力ツリー
        self.output_file_name (str): 出力ファイル名
        self.output_file (ROOT.TFile): 出力ファイル
    """

    def __init__(self,input_file_name,args):
        """
        Args :
            input_file_name (str): ファイル名
            args (argparse.Namespace) : parser.parse_args() の戻り値
        """

        super().__init__( input_file_name, args,\
            intree=args.intree, outdir=args.outdir, nentries=args.nentries,\
            printfreq=args.printfreq, verbose=args.verbose )
        """VANLModule.__init__

        モジュールのコンストラクタ
        例ではコマンドライン引数(args)から初期値を読み取っているが、直接指定することもできる
        例えば、intree='eventtree' などとする

        Args :
            input_file_name (str):
            args (argparse.Namespace):
            intree (str): ツリー名 (default='tree')
            outdir (str): 出力ディレクトリ (default:'.')
            nentries (int): 読み込むエントリー数。負の場合、全エントリー (default:-1)
            printfreq (int): 進捗を表示する頻度(エントリー数) (default=10)
            verbose (int): メッセージを表示するレベル (default=0)
        """

    def user_output_basename(self,file_name) :
        """
        出力するファイル名を指定する関数
        注意 : .root やディレクトリ名がつかないのを返すようにする

        Args :
            file_name (str): 入力ファイル名

        Returns :
            str: 出力ファイル名(拡張子、ディレクトリなし)
        """
        base = os.path.basename( file_name )
        name, ext = os.path.splitext( base )
        return name+'_spect'

    def user_event_routine(self,current_entry) :
        """
        ツリーのエントリーごとに呼ばれる関数
        この関数が呼ばれた時点で GetEntry(current_entry) は完了している

        解析結果ごとに最後に呼ぶ関数が異なる
        1. 正常終了の場合 :
            return self.ok_event()
        2. 現在のイベントのみ抜ける場合 :
            return self.skip_event()
        3. ループを抜ける場合 :
            return self.quit_loop()

        Args :
            current_entry (int): 現在のエントリー番号

        Returns :
            AnalysisStatus:
        """

        if evs.when( self.input_tree.nhits == 0, set_flag='No_Hit_Event',\
            otherwise_set_flag='Hit_Exist_Event' ) :
            return self.skip_event()
        """evs.when

        フラグの定義と計上を行う関数
        プログラムの終了時に各フラグのカウント数が表示される

        各引数については、Args の通り
        フラグ set_flag が None でなく未定義の場合、condition の真偽に関わらず、定義する
        otherwise_set_flag についても同様

        上記の例では、
        1. self.input_tree.nhits == 0 (condition=True) の場合 :
            'No_Hit_Event' のフラグを立て、このイベントをスキップする (return self.skip_event())
        2. self.input_tree.nhits != 0 (condition=False) の場合 :
            'Hit_Exist_Event' のフラグを立て、このイベントの解析を続ける

        Args :
            condition (bool): 条件式
            set_flag (str): condition が True の場合に立てるフラグ。未指定時は何もしない。(default:None)
            otherwise_set_flag (str): 同じく condition が False の場合に立てるフラグ。(default:None)

        Returns :
            bool: condition をそのまま戻す
        """

        etotal = self.input_tree.etotal

        if evs.when( etotal < self.args.ewindow[0] or self.args.ewindow[1] < etotal,\
            otherwise_set_flag='In_Energy_Range' ) :
            return self.skip_event()

        self.spect.Fill( self.input_tree.etotal )
        return self.ok_event()

    def user_before_loop(self) :
        """
        ループを開始する前に一度だけ呼ばれる関数
        ヒストグラムの定義などを行う

        戻り値によってその後の動作が異なる
        1. 関数を正常終了し、ループを開始する場合 :
            return self.ok_before_loop()
        2. 問題が生じたため、ループを開始せずソフトを終了する場合 :
            return self.error_before_loop()

        Returns :
            AnalysisStatus:
        """

        if self.open_files() is self.error_before_loop() :
            return self.error_before_loop()
        """self.open_files

        入力ファイルの展開、ツリーの読み込み、出力ファイルの作成を行う
        いずれかの処理で問題を生じた場合は self.error_before_loop() を返す
        基本的にここは変更しない
        """

        self.spect = TH1D( 'spect', 'etotal;keV', 200, -0.5, 199.5 )

        return self.ok_before_loop()

    def user_after_loop(self) :
        """
        ループ終了後に一度だけ呼ばれる関数
        ヒストグラムの保存などを行う
        最後に self.ok_after_loop を呼ぶ
        """

        self.output_file.cd()
        self.spect.Write()
        self.output_file.Close()

        return self.ok_after_loop()

if __name__ == '__main__':

    parser = usage()
    args = parser.parse_args()

    if hasattr( args, 'outdir' ) :
        os.makedirs( args.outdir, exist_ok=True )
    gROOT.SetBatch( True )
    gROOT.ProcessLine( 'gErrorIgnoreLevel = kFatal;' )

    for file in args.file:

        start = time.time()

        ana = user_analysis( file, args )
        ana.run_analysis()
        """anlpy2.analysis_framework.VANLModule.run_analysis

        ループを開始する関数
        おおざっぱにいえば、
            1. user_before_loop
            2. ループ( user_event_routine を N 回)
            3. user_after_loop
        の順で関数を呼ぶ
        """

        end = time.time()
        print( f' Processed Time : {end-start:.3f} [sec]' )

    os.system( f"osascript -e 'display notification \"{parser.prog:s}: Process is finished\"'" )

```
