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

from Tokenize import Tokenize
from Linter import Linter

class ArgParser:

    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Turquoise: VHDL Linter + Compilation Toolchain')
        g = self.parser.add_mutually_exclusive_group()
        g.add_argument("-a", "--analyze", metavar='path', help="analyze VHDL file(s)")
        g.add_argument("-c", "--compile", metavar='path', help="compile VHDL file(s)")
        g.add_argument("-l", "--lint", metavar='path', help="lint VHDL file(s)")
        g.add_argument("-w", "--wave", nargs=2, metavar=('path', 'unit'), type=str, help="generate waveform of VHDL unit")
        g.add_argument("-u", "--upload", nargs=2, metavar=('path', 'unit'), help="upload VHDL unit to board")

        args = self.parser.parse_args()

        if args.analyze:
            self._analyze_file_dir(args.analyze)

        # Compile file/dir of files
        elif args.compile:
            if os.path.isfile(args.compile):
                self._compile_file(args.compile)
            elif os.path.isdir(args.compile):
                files = [y for x in os.walk(args.compile) for y in glob(os.path.join(x[0], '*.vhdl'))]
                for f in files:
                    self._compile_file(f)
            else:
                print('Invalid file/dir path.')

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
            if os.path.isfile(args.lint):
                self._lint_file(args.lint)
            elif os.path.isdir(args.lint):
                files = [y for x in os.walk(args.lint) for y in glob(os.path.join(x[0], '*.vhdl'))]
                for f in files:
                    self._lint_file(f)
            else:
                print('Invalid file/dir path.')


    def _analyze_file(self, filename):
        cmd = "./dist/fpga-toolchain/bin/ghdl -a " + "\'" + filename + "\'"
        print('Analyzing file ' + filename + ' ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode == 0:
            print('Finished analyzing successfully!')
        print()


    def _analyze_file_dir(self, path):
        if os.path.isfile(path):
            self._analyze_file(path)
        elif os.path.isdir(path):
            files = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.vhdl'))]
            for f in files:
                self._analyze_file(f)
        else:
            print('Invalid file/dir path.')


    def _compile_file(self, filename):
        cmd = "./dist/fpga-toolchain/bin/ghdl -c " + "\'" + filename + "\'"
        print('Compiling file ' + filename + ' ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode == 0:
            print('Finished compiling successfully!')
        print()


    def _elaborate_unit(self, unitname):
        cmd = "./dist/fpga-toolchain/bin/ghdl -e " + unitname
        print('Elaborating unit ' + unitname + ' ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode != 0:
            exit(1)
        print('Finished elaborating successfully!\n')


    def _elaborate_run_unit(self, unitname):
        cmd = "./dist/fpga-toolchain/bin/ghdl -r " + unitname + " --vcd=" + unitname + ".vcd"
        print('Running unit ' + unitname + ' ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode != 0:
            exit(1)
        print('Finished elaborating and running successfully!\n')


    def _run_gtkwave(self, filename):
        cmd = "./dist/gtkwave/Contents/MacOS/gtkwave -o " + filename
        print('Opening ' + filename + ' in gtkwave ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode != 0:
            exit(1)
        print('Closing gtkwave!\n')


    def _run_file(self, unitname):
        self._elaborate_unit(unitname)
        self._elaborate_run_unit(unitname)
        self._run_gtkwave(unitname + ".vcd")


#export GHDL_PREFIX=/absolute/path/to/here/fpga-toolchain/lib/ghdl
#./fpga-toolchain/bin/yosys -q -p 'ghdl --std=08 Examples/FlashingLED/top.vhdl Examples/FlashingLED/counter.vhdl -e top; synth_ice40 -json Examples/FlashingLED/top.json'
#./fpga-toolchain/bin/nextpnr-ice40 --up5k --package sg48 --pcf Examples/FlashingLED/top.pcf --asc Examples/FlashingLED/top.asc --json Examples/FlashingLED/top.json
#./fpga-toolchain/bin/icepack Examples/FlashingLED/top.asc Examples/FlashingLED/top.bin
#./fpga-toolchain/bin/iceprog Examples/FlashingLED/top.bin

    def _synthesize_unit(self, filepath, unitname):
        cmd = "./dist/fpga-toolchain/bin/yosys -q -p \'ghdl --std=08 "
        if os.path.isfile(filepath):
            cmd = cmd + path + " "
        elif os.path.isdir(filepath):
            files = [y for x in os.walk(filepath) for y in glob(os.path.join(x[0], '*.vhdl'))]
            for f in files:
                cmd = cmd + f + " "
        cmd = cmd  + "-e " + unitname + "; synth_ice40 -json " + filepath + "/" + unitname + ".json\'"
        print(cmd)

        print('Synthesizing ' + unitname + ' ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode != 0:
            exit(1)
        print('Finished synthesizing successfully!\n')


    def _route_unit(self, filepath, unitname):
        cmd = "./dist/fpga-toolchain/bin/nextpnr-ice40 --up5k --package sg48 --pcf " + filepath + "/" + unitname + \
        ".pcf --asc " + filepath + "/" + unitname + ".asc --json " + filepath + "/" + unitname + ".json --top " + unitname
        print('Routing ' + unitname + ' ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode != 0:
            exit(1)
        print(returned_value)
        print('Finished routing successfully!\n')


    def _generate_bitstream(self, filepath, unitname):
        cmd = "./dist/fpga-toolchain/bin/icepack " + filepath + "/" + unitname + ".asc " + filepath + "/" + unitname + ".bin"
        print('Generating bitstream for ' + unitname + ' ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode != 0:
            exit(1)
        print('Finished generating bitstream successfully!\n')


    def _flash_fpga(self, filepath, unitname):
        cmd = "./dist/fpga-toolchain/bin/iceprog " + filepath + "/" + unitname + ".bin"
        print('Flashing ' + unitname + ' to FPGA ...')
        returned_value = subprocess.run(cmd, shell=True)
        if returned_value.returncode != 0:
            exit(1)
        print('Finished flashing successfully!\n')


    def _upload_file(self, filepath, unitname):
        self._synthesize_unit(filepath, unitname)
        self._route_unit(filepath, unitname)
        self._generate_bitstream(filepath, unitname)
        self._flash_fpga(filepath, unitname)


    def _lint_file(self, filename):
        print('Linting ' + filename + ' ...')
        linter = Linter(filename)
        linter.lint()
        logger = linter.get_logger()
        logger.print_logs_to_terminal()
        if len(logger.get_logs()) == 0:
            print('Finished linting successfully!')
        print()
