-- Expect 'test_mismatch_entity', got 'test_mismatch_entity_'

entity test_mismatch_entity is
	port(
		SIG1 : in  std_logic_vector(0 to 3);
		SIG2 : in  std_logic_vector(1 downto 0);
        SIG3 : out std_logic_vector(0 to 3)
	);
end test_mismatch_entity_;