#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: ArgParser.py
#
#  Description: Implementation of argument parser module.
#  Check README.md for CLI usage.
#
# -----------------------------------------------------------------------------
import argparse
import sys
import subprocess
import os
from glob import glob

from .Tokenize import Tokenize
from .Linter import Linter
from .Messages import pp

class App:

    def __init__(self, _logger):
        self._logger = _logger
        self._parser = argparse.ArgumentParser(
            description='Turquoise: VHDL Linter + Compilation Toolchain'
        )

        g = self._parser.add_mutually_exclusive_group()
        g.add_argument("-a", "--analyze", metavar='path', help="analyze VHDL file(s)")
        g.add_argument("-c", "--compile", metavar='path', help="compile VHDL file(s)")
        g.add_argument("-l", "--lint", metavar='path', help="lint VHDL file(s)")
        g.add_argument("-w", "--wave", nargs=2, metavar=('path', 'unit'),
                       type=str, help="generate waveform of VHDL unit")
        g.add_argument("-u", "--upload", nargs=2, metavar=('path', 'unit'),
                       help="upload VHDL unit to board")
        g.add_argument("-x", "--clean", action='store_true',
                       help="clean compiled binaries and waveforms")

        args = self._parser.parse_args()

        if args.analyze:
            self._analyze_file_dir(args.analyze)

        # Compile file/dir of files
        elif args.compile:
            if os.path.isfile(args.compile):
                self._compile_file(args.compile)
            elif os.path.isdir(args.compile):
                files = [y for x in os.walk(args.compile)
                           for y in glob(os.path.join(x[0], '*.vhd[l]'))]
                for f in files:
                    self._compile_file(f)
            else:
                pp('error', 'Invalid file/dir path.')

        # Analyze, elaborate, run required files, and simulate unit on gtkwave
        elif args.wave:
            self._analyze_file_dir(args.wave[0])
            self._run_file(args.wave[1])

        # Upload unit to board
        elif args.upload:
            self._analyze_file_dir(args.upload[0])
            self._upload_file(args.upload[0], args.upload[1])

        # Lint file/dir of files
        elif args.lint:
            pp('info', 'Running "turquoise" linter ...')
            if os.path.isfile(args.lint):
                self._lint_files([args.lint])
            elif os.path.isdir(args.lint):
                files = [y for x in os.walk(args.lint)
                           for y in glob(os.path.join(x[0], '*.vhd[l]'))]
                self._lint_files(files)
            else:
                pp('error', 'Failed to lint - Invalid file/dir path.')

        # @TODO: Clean up project
        elif args.clean:
            self._clean()


    def _analyze_file(self, filename):
        cmd = "./dist/fpga-toolchain/bin/ghdl -a " + "\'" + filename + "\'"
        pp('info', 'Analyzing file ' + filename + ' ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode == 0:
            pp('success', 'Finished analyzing successfully!')


    def _analyze_file_dir(self, path):
        if os.path.isfile(path):
            self._analyze_file(path)
        elif os.path.isdir(path):
            files = [y for x in os.walk(path)
                       for y in glob(os.path.join(x[0], '*.vhd[l]'))]
            for f in files:
                self._analyze_file(f)
        else:
            pp('error', 'Failed to analyze file directory - Invalid file/dir path.')


    def _compile_file(self, filename):
        cmd = "./dist/fpga-toolchain/bin/ghdl -c " + "\'" + filename + "\'"
        pp('info', 'Compiling file ' + filename + ' ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode == 0:
            pp('success', 'Finished compiling successfully!')


    def _elaborate_unit(self, unitname):
        cmd = "./dist/fpga-toolchain/bin/ghdl -e " + unitname

        pp('info', 'Elaborating unit ' + unitname + ' ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode != 0:
            exit(1)
        pp('success', 'Finished elaborating successfully!')


    def _elaborate_run_unit(self, unitname):
        cmd = "./dist/fpga-toolchain/bin/ghdl -r " + unitname + " --vcd=" + unitname + ".vcd"
        pp('info', 'Running unit ' + unitname + ' ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode != 0:
            exit(1)
        pp('success', 'Finished elaborating and running successfully!')


    def _run_gtkwave(self, filename):
        cmd = "./dist/gtkwave/Contents/MacOS/gtkwave -o " + filename
        pp('info', 'Opening ' + filename + ' in gtkwave ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode != 0:
            exit(1)
        pp('info', 'Closing gtkwave!')


    def _run_file(self, unitname):
        self._elaborate_unit(unitname)
        self._elaborate_run_unit(unitname)
        self._run_gtkwave(unitname + ".vcd")


    def _export_ghdl_path(self):
        abspath = os.path.abspath("fpga-toolchain/lib/ghdl")
        cmd = "export GHDL_PREFIX=" + abspath
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode != 0:
            exit(1)
        pp('info', 'Set GHDL export path successfully!')


    def _synthesize_unit(self, filepath, unitname):
        cmd = "./dist/fpga-toolchain/bin/yosys -q -p \'ghdl --std=08 "
        if os.path.isfile(filepath):
            cmd = cmd + path + " "
        elif os.path.isdir(filepath):
            files = [y for x in os.walk(filepath) for y in glob(os.path.join(x[0], '*.vhd[l]'))]
            for f in files:
                cmd = cmd + f + " "
        cmd = cmd  + "-e " + unitname + "; synth_ice40 -json " + filepath + "/" + unitname + ".json\'"

        pp('info', 'Synthesizing ' + unitname + ' ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode != 0:
            exit(1)
        pp('success', 'Finished synthesizing successfully!')


    def _clean(self):
        pp('info', 'Cleaning current project ...')
        vcd_files = [y for x in os.walk('.')
                       for y in glob(os.path.join(x[0], '*.vcd'))]
        fst_files = [y for x in os.walk('.')
                       for y in glob(os.path.join(x[0], '*.vcd.fst'))]
        cf_files  = [y for x in os.walk('.')
                       for y in glob(os.path.join(x[0], '*.cf'))]

        files_to_be_deleted = vcd_files + fst_files + cf_files

        for f in files_to_be_deleted:
            cmd = "rm -rf " + f
            returned_value = subprocess.run(cmd, shell=True)
            if returned_value.returncode != 0:
                pp('error', 'Fail to delete file "' + f + '"')
                exit(1)

        pp('success', 'Current project is successfully cleaned')


    def _route_unit(self, filepath, unitname):
        cmd = "./dist/fpga-toolchain/bin/nextpnr-ice40 --up5k --package sg48 --pcf " + \
              filepath + "/" + unitname + \
              ".pcf --asc " + filepath + "/" + unitname + ".asc --json " + filepath + \
              "/" + unitname + ".json --top " + unitname
        pp('info', 'Routing ' + unitname + ' ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode != 0:
            exit(1)
        pp('info', returned_value)
        pp('success', 'Finished routing successfully!')


    def _generate_bitstream(self, filepath, unitname):
        cmd = "./dist/fpga-toolchain/bin/icepack " + filepath + "/" + \
               unitname + ".asc " + filepath + "/" + unitname + ".bin"
        pp('info', 'Generating bitstream for ' + unitname + ' ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode != 0:
            exit(1)
        pp('success', 'Finished generating bitstream successfully!')


    def _flash_fpga(self, filepath, unitname):
        cmd = "./dist/fpga-toolchain/bin/iceprog " + filepath + "/" + unitname + ".bin"
        pp('info', 'Flashing ' + unitname + ' to FPGA ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode != 0:
            exit(1)
        pp('success', 'Finished flashing successfully!')


    def _upload_file(self, filepath, unitname):
        self._export_ghdl_path()
        self._synthesize_unit(filepath, unitname)
        self._route_unit(filepath, unitname)
        self._generate_bitstream(filepath, unitname)
        self._flash_fpga(filepath, unitname)


    def _lint_files(self, _filenames):
        linter = Linter(_filenames, self._logger)
        linter.lint()
        logger = linter.print_status()