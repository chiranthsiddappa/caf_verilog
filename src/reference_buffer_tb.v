`timescale 1ns/1ns
`define NULL 0

module reference_buffer_tb();
   reg clk;
   integer write_file;
   reg     m_axis_tready;
   reg     m_axis_index_tvalid;
   reg     m_axis_index_tdata;
   wire    s_axis_data_tready;
   wire [{{ i_bits - 1}}:0] i;
   wire [{{ q_bits - 1}}:0] q;
   wire                     s_axis_data_tvalid;

   initial begin
      clk = 1'b0;
   end

   {% include "reference_buffer_inst.v" %}

     always begin
        #10 clk = ~clk;
     end
   
endmodule // reference_buffer_tb

