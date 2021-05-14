# Turquoise

VHDL linter and compilation toolchain for the FPGA Upduino V3 board

## Installing

1) Make sure your system supports python3.
2) Install the python libraries `colored` and `pyVHDLParser` using pip. You can read more about this here if you do not already have pip installed: https://pip.pypa.io/en/stable/installing/
3) Download the project as a .zip file from the main branch of this repo and unzip it.
4) Inside the `dist` directory, unzip gtkwave.zip.
5) Download the fpga-toolchain as a zipped file: https://drive.google.com/file/d/1cnvAypqYposi_YmEpbKnw8qrSvT3U0Ln/view?usp=sharing
6) Unzip it and move it under the `dist` directory alongside the gtkwave folder.
7) You're all set!

## Running

1) To launch the application, cd into the `turquoise-master` directory and run the command `python3 . -h`.
2) You can run the compiler on the examples we have provided using the command `python3 . -c Examples`. You can also provide the path to a single file instead of an entire directory such as `python3 . -c Examples/AND2/AND2.vhdl`. The same applies for analyzing with the `-a` flag and the linter with the `-l` flag. Make sure that the directory that contains your code is somwhere inside the turquoise-blue folder.
3) When generating waveforms, the provided path must contain all the files needed to successfully run the simulation. The unit name is the name of the entity that you are running the simulation on.
4) Same applies to uploading code to the board. Make sure the Upduino board is connected to your computer and that your .pcf file is in the same directory as the rest of your code. The unit name is the name of the top-level entity that you are uploading to the board.

## Linter features supported

The following linter features are currently supported with the Turquoise VHDL Linter:

For more examples of the linter capabilities, please refer to the `examples` folder

- Syntax check
	- `turquoise` supports full syntax check for the 1987, 1993, 2002 versions of the IEEE 1076 VHDL standard (and partially the latest 2008 revision) through `ghdl` front-end.

- Primitives check
	 - `turquoise` performs syntax and semantic check for certain primitive types and displays errors, warning, and info when necessary
	 - Current primitives supported includes
	   `std_logic, std_logic_vector, bit, signed, unsigned, integer, 	boolean, time, string`
	 - Example: for the following snippet, the linter returns this warning
		 ```
		 entity top is
		port(
			SIG : out unsigned(2 downto 0);
	        BTN : in std_logic_vector(1 to 0)
		);
		end top;
		
		>>> WARNING: (line:   4, col: 31) @ a.txt: Expecting first value to be smaller than second value in "to" declaration for STD_LOGIC_VECTOR
		 ```

- Entity/Component typecheck
	- `turquoise` performs signals type check when comparing `entity` declaration and `component` instantiation, and displays errors, warning, and info when necessary
	- @TODO: Add example

- Port map typecheck
	- `turquoise` performs signals type check when mapping signals in `port map` declaration, and displays errors, warning, and info when necessary
	- @TODO: Add example

- Signals declared but not used
	- @TODO: Add example 

- Signals assigned but not declared
	- @TODO: Add example

- Deprecated package
	- @TODO: Add example

- Duplicated package import
	- @TODO: Add example



## Compilation toolchain usage

@TODO add more specifics for each command
The following options are available with the Turquoise VHDL Linter + Compilation Toolchain:

```
usage: . [-h] [-a path | -c path | -l path | -w path unit | -u path unit | -x]

Turquoise: VHDL Linter + Compilation Toolchain

optional arguments:
  -h, --help            show this help message and exit
  -a path, --analyze path
                        syntax check VHDL file(s) using GHDL front-end
  -c path, --compile path
                        compile VHDL file(s)
  -l path, --lint path  lint VHDL file(s)
  -w path unit, --wave path unit
                        generate waveform of VHDL unit
  -u path unit, --upload path unit
                        upload VHDL unit to board
  -x, --clean           clean compiled binaries and waveforms
```

## Authors

* [Trung Truong](https://github.com/ttrung149)
* [Athokshay Ashok](https://github.com/aashok3)
* [Siegfred Madeghe](https://github.com/ZiggyZiggyD)

## Contributing

Fork the repo and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details
