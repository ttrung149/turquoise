# Turquoise

VHDL linter and compilation toolchain for the FPGA Upduino V3 board

## Installing

Clone the repository

## Linter features supported

## Authors

* [Trung Truong](https://github.com/ttrung149)
* [Athokshay Ashok](https://github.com/aashok3)

## Contributing

Fork the repo and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details



Here are the following options available with the VHDL Linter + Compilation Toolchain:

- To compile a file, use the command 'python3 vhdl-lint.py -c filepath'
or 'python3 vhdl-lint.py --compile filepath'. You can also provide the path of a directory, and the command will compile every VHDL file in the directory recursively.

- To run and simulate a testbench file, first anayze every file required for the testbench, including the testbench file, using the command:
'python3 vhdl-lint.py -a filepath' or 'python3 vhdl-lint.py --analyze filepath'. Then use the command 'python3 vhdl-lint.py -r unitname'. The unitname is the entity name of the testbench file.

You can also analyze multiple files at once by providing the path of a directory instead of a single file. However, when running a file, you can only provide one single unit name.
