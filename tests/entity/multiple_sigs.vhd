entity test_mismatch_entity is
    generic(
		HELLO, WORLD : std_logic_vector(0 to 3);
        TEST1, TEST2, TEST3 : std_logic_vector(0 to 4)
	);
	port(
		SIG1, SIG2, SIG3 : in  std_logic_vector(0 to 3);
        SIG4, SIG5, SIG6 : out std_logic_vector(0 to 6)
	);
end test_mismatch_entity;