library ieee;
use ieee.std_logic_1164.all;

entity AND2 is
    generic (
        delay: time := 10 ns;
        str: string := "hello world"
    );
    port( 
        in0: in std_logic;
        in1: in std_logic;
        output: out std_logic
    );
end AND2;

entity AND2_tb is
end AND2_tb;

architecture AND2_tb of AND2_tb is

    --invoke the AND2 component 
    component AND2
        generic (
            delay: integer;
            str: std_logic_vector(3 downto 0)
        );
        port( 
            in0: in std_logic;
            in1: in std_logic;
            output: out std_logic
        );
    end component;

    --define signals 
    signal in0 : std_logic := '0';
    signal in1 : std_logic := '0';
    signal output : std_logic;

begin
    uut: AND2 port map (in0, in1, output);
    stim_proc: process
    
    -- simulate the truth table behavior
    begin  
        wait for 10 ns;
        -- signals use <= to assign values
        in0 <= '0';
        in1 <= '0';
    
        -- wait for M ns, gives a duration to the values
        wait for 50 ns; 
        in0 <= '0';
        in1 <= '1';

        wait for 50 ns; 
        in0 <= '1';
        in1 <= '0';

        wait for 50 ns; 
        in0 <= '1';
        in1 <= '1';

        wait;
    end process;
end;
    