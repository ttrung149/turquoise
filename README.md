# Turquoise

VHDL linter and compilation toolchain for the FPGA Upduino V3 board

## Installing

1) Install the python libraries `colored` and `pyVHDLParser` using pip.
2) Download the project as a .zip file from the main branch of this repo and unzip it.
3) Inside the `dist` directory, unzip gtkwave.zip.
4) Download the fpga-toolchain as a zipped file: https://drive.google.com/file/d/1cnvAypqYposi_YmEpbKnw8qrSvT3U0Ln/view?usp=sharing
5) Unzip it and move it under the `dist` directory alongside the gtkwave folder.

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
