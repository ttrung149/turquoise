-- and gate testbench structural modeling 
-- add the standard library packages
library ieee;
use ieee.std_logic_1164.all;

-- define the empy entity for testbench
entity OR2_tb is
end OR2_tb;

ARCHITECTURE OR2_tb OF OR2_tb IS

    --invoke the OR2 component 
    COMPONENT OR2
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
 uut: OR2 PORT MAP (in0, in1, output);
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