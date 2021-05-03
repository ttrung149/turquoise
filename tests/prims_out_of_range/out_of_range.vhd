entity test_out_of_range is
	port(
		SIG1 : out std_logic_vector(23 to 1);    -- out of range std_logic_vector
		SIG2 : out std_logic_vector(0 downto 1); -- out of range std_logic_vector
		SIG3 : out signed(23 to 1);    			 -- out of range signed
		SIG4 : out signed(0 downto 1); 			 -- out of range signed
		SIG5 : out unsigned(23 to 1);    		 -- out of range unsigned
		SIG6 : out unsigned(0 downto 1) 		 -- out of range unsigned
	);
end test_out_of_range;

component test_out_of_range
	port(
		SIG1 : out std_logic_vector(23 to 1);    -- out of range std_logic_vector
		SIG2 : out std_logic_vector(0 downto 1); -- out of range std_logic_vector
		SIG3 : out signed(23 to 1);    			 -- out of range signed
		SIG4 : out signed(0 downto 1); 			 -- out of range signed
		SIG5 : out unsigned(23 to 1);    		 -- out of range unsigned
		SIG6 : out unsigned(0 downto 1) 		 -- out of range unsigned
	);
end component;