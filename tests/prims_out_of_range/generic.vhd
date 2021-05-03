entity test_generic is
    generic (
        SIG1 : std_logic_vector(23 to 1);        -- out of range std_logic_vector
		SIG2 : std_logic_vector(0 downto 1);     -- out of range std_logic_vector
		SIG3 : signed(23 to 1);    			     -- out of range signed
		SIG4 : signed(0 downto 1); 			     -- out of range signed
		SIG5 : unsigned(23 to 1);    		     -- out of range unsigned
		SIG6 : unsigned(0 downto 1) 		     -- out of range unsigned
    );

	port(
		SIG1 : out std_logic_vector(23 to 1);    -- out of range std_logic_vector
		SIG2 : out std_logic_vector(0 downto 1); -- out of range std_logic_vector
		SIG3 : out signed(23 to 1);    			 -- out of range signed
		SIG4 : out signed(0 downto 1); 			 -- out of range signed
		SIG5 : out unsigned(23 to 1);    		 -- out of range unsigned
		SIG6 : out unsigned(0 downto 1) 		 -- out of range unsigned
	);
end test_generic;

component test_generic is
    generic (
        SIG1 : std_logic_vector(23 to 1);        -- out of range std_logic_vector
		SIG2 : std_logic_vector(0 downto 1);     -- out of range std_logic_vector
		SIG3 : signed(23 to 1);    			     -- out of range signed
		SIG4 : signed(0 downto 1); 			     -- out of range signed
		SIG5 : unsigned(23 to 1);    		     -- out of range unsigned
		SIG6 : unsigned(0 downto 1) 		     -- out of range unsigned
    );

	port(
		SIG1 : out std_logic_vector(23 to 1);    -- out of range std_logic_vector
		SIG2 : out std_logic_vector(0 downto 1); -- out of range std_logic_vector
		SIG3 : out signed(23 to 1);    			 -- out of range signed
		SIG4 : out signed(0 downto 1); 			 -- out of range signed
		SIG5 : out unsigned(23 to 1);    		 -- out of range unsigned
		SIG6 : out unsigned(0 downto 1) 		 -- out of range unsigned
	);
end component;