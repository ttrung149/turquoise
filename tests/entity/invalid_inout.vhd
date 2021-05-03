-- Expect 'in', 'out', 'inout', 'buffer'

entity test_invalid_inout_entity is
	port(
		SIG1 : in_  std_logic_vector(0 to 3);
		SIG2 : out_  std_logic_vector(1 downto 0);
        SIG3 : inout_ std_logic_vector(0 to 3);
        SIG4 : buffer_ std_logic
	);
end test_invalid_inout_entity;