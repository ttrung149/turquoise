--implementing an AND gate
-- behavioral model based on the truth table
-- this AND gate has two input with std_logic type and widt of 1 bit : in1 and in2
-- this AND gate has 1 output port from type std_logic with 1 bit width
-----------------------------------------

--include ieee libaries
library ieee;
use ieee.std_logic_1164.all;

-----------------------------------------
-- define AND2 entity with its input and output ports
entity AND2 is
port( 
in0: in std_logic;
in1: in std_logic;
output: out std_logic
);
end AND2;

------------------------------------------
architecture dataflow of AND2 is 
begin 

    output <= in0 and in1; 

end dataflow;