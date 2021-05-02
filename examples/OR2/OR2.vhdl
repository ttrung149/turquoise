--implementing an OR gate
-- behavioral model based on the truth table
-- this OR gate has two input with std_logic type and widt of 1 bit : in1 and in2
-- this OR gate has 1 output port from type std_logic with 1 bit width
-----------------------------------------

--include ieee libaries
library ieee;
use ieee.std_logic_1164.all;

-----------------------------------------
-- define OR2 entity with its input and output ports
entity OR2 is
port( 
in0: in std_logic;
in1: in std_logic;
output: out std_logic
);
end OR2;

------------------------------------------
architecture dataflow of OR2 is 
begin 

    output <= in0 or in1; 

end dataflow;