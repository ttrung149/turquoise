library ieee;
use ieee.std_logic_1164.all;

entity OR2
PORT(
    in0 : IN  std_logic;
    in1 : IN  std_logic;
    output : OUT  std_logic
    );
END OR2;

-- define the empy entity for testbench
entity OR2_tb is
end OR2_tb;

ARCHITECTURE OR2_tb OF OR2_tb IS
    COMPONENT OR2
    PORT(
        in0 : IN  std_logic;
        in1 : IN  std_logic;
        output : OUT  std_logic
        );
    END COMPONENT;

    --define signals 
    signal in0, in2, in3 : std_logic := '0';
    signal in1 : std_logic := '0';
    signal output : std_logic;
    constant MAX_SIM: time := 50 * PERIOD;

BEGIN
uut: AND2 PORT MAP (in0, in1, output);
    stim_proc: process

    -- simulate the truth table behavior
    begin  
        wait for 10 ns;
        -- signals use <= to assign values
        not_declared <= '0';
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