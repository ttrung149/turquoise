-- and gate testbench structural modeling 
-- add the standard library packages
library ieee;
use ieee.std_logic_1164.all;

-- define the empy entity for testbench
entity AND2_tb is
end AND2_tb;

ARCHITECTURE AND2_tb OF AND2_tb IS

    --invoke the AND2 component 
    COMPONENT AND2
    PORT(
        in0 : IN  std_logic;
        in1 : IN  std_logic;
        output : OUT  std_logic
        );
    END COMPONENT;

    --define signals 
   signal in0 : std_logic := '0';
   signal in1 : std_logic := '0';
   signal output : std_logic;


BEGIN
 uut: AND2 PORT MAP (in0, in1, output);
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

END;