import argparse
from Tokenize import Tokenize
import sys
import subprocess
import os
from glob import glob
from Linter import Linter

class ArgParser:

	def __init__(self):

		#Create ArgParse with options
		self.parser = argparse.ArgumentParser(description='VHDL Linter + Compilation Toolchain')
		g = self.parser.add_mutually_exclusive_group()
		g.add_argument("-t", "--tokenize", metavar='path', help="tokenize VHDL file")
		g.add_argument("-a", "--analyze", metavar='path', help="analyze VHDL file")
		g.add_argument("-c", "--compile", metavar='path', help="compile VHDL file")
		g.add_argument("-l", "--lint", metavar='path', help="lint VHDL file")
		g.add_argument("-r", "--run", metavar='unit', help="run VHDL unit with gtkwave")
		g.add_argument("-u", "--upload", metavar='path', help="upload VHDL file to board")

		args = self.parser.parse_args()

		#Tokenize
		if args.tokenize:
			if os.path.isfile(args.tokenize):
				tokenize = Tokenize(args.tokenize)
				tokens = tokenize.get_tokens()
				print(tokens)
			else:
				print('Invalid file path')

		#Analyze file/list of files
		elif args.analyze:
			if os.path.isfile(args.analyze):
				self._analyze_file(args.analyze)
			elif os.path.isdir(args.analyze):
				files = [y for x in os.walk(args.analyze) for y in glob(os.path.join(x[0], '*.vhdl'))]
				for f in files:
					self._analyze_file(f)
			else:
				print('Invalid file/dir path.')

		#Compile file/list of files
		elif args.compile:
			if os.path.isfile(args.compile):
				self._compile_file(args.compile)
			elif os.path.isdir(args.compile):
				files = [y for x in os.walk(args.compile) for y in glob(os.path.join(x[0], '*.vhdl'))]
				for f in files:
					self._compile_file(f)
			else:
				print('Invalid file/dir path.')

		#Elaborate, run, simulate unit on gtkwave
		elif args.run:
			self._run_file(args.run)

		#Upload file to board
		elif args.upload:
			self._upload_file(args.upload)

		#Lint file/list of files
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
		cmd = "./fpga-toolchain/bin/ghdl -a " + "\'" + filename + "\'"
		print('Analyzing file ' + filename + ' ...')
		returned_value = subprocess.run(cmd, shell=True)
		if returned_value.returncode == 0:
			print('Finished analyzing successfully!')
		print()


	def _compile_file(self, filename):
		cmd = "./fpga-toolchain/bin/ghdl -c " + "\'" + filename + "\'"
		print('Compiling file ' + filename + ' ...')
		returned_value = subprocess.run(cmd, shell=True)
		if returned_value.returncode == 0:
			print('Finished compiling successfully!')
		print()


	def _elaborate_unit(self, unitname):
		cmd = "./fpga-toolchain/bin/ghdl -e " + unitname
		print('Elaborating unit ' + unitname + ' ...')
		returned_value = subprocess.run(cmd, shell=True)
		if returned_value.returncode == 1:
			exit(1)
		print('Finished elaborating successfully!\n')


	def _elaborate_run_unit(self, unitname):
		cmd = "./fpga-toolchain/bin/ghdl -r " + unitname + " --vcd=" + unitname + ".vcd"
		print('Running unit ' + unitname + ' ...')
		returned_value = subprocess.run(cmd, shell=True)
		if returned_value.returncode == 1:
			exit(1)
		print('Finished elaborating and running successfully!\n')


	def _run_gtkwave(self, filename):
		cmd = "./gtkwave/Contents/MacOS/gtkwave -o " + filename
		print('Opening ' + filename + ' in gtkwave ...')
		returned_value = subprocess.run(cmd, shell=True)
		if returned_value.returncode == 1:
			exit(1)
		print('Closing gtkwave!\n')


	def _run_file(self, unitname):
		self._elaborate_unit(unitname)
		self._elaborate_run_unit(unitname)
		self._run_gtkwave(unitname + ".vcd")


	def _upload_file(self, filename):
		print('Uploading ' + filename + ' to board ...')


	def _lint_file(self, filename):
		print('Linting ' + filename + ' ...')
		linter = Linter(filename)
		linter.lint()
		logger = linter.get_logger()
		logger.print_logs_to_terminal()
		if len(logger.get_logs()) == 0:
			print('Finished linting successfully!')
		print()
