library ieee;
use ieee.std_logic_1164.all;

entity test_duplicated_entity is
	generic (
        DELAY: time := 10 ns
    );
	port(
		SIG1 : in  std_logic_vector(0 to 3);
		SIG2 : in  std_logic_vector(1 downto 0);
        SIG3 : out std_logic_vector(0 to 3)
	);
end test_duplicated_entity;

entity test_duplicated_entity is
    generic (
        DELAY: time := 10 ns
    );

	port(
		SIG1 : in  std_logic_vector(0 to 3);
		SIG2 : in  std_logic_vector(1 downto 0);
        SIG3 : out std_logic_vector(0 to 3)
	);
end test_duplicated_entity;