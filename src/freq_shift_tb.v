`timescale 1ns/1ns
`define NULL 0

module freq_shift_tb();
   reg clk;
   reg m_axis_tvalid;
   reg [{{phase_bits - 1}}:0] freq_step;
   reg [{{i_bits - 1}}:0]     xi;
   reg [{{q_bits - 1}}:0]     xq;
   wire                       s_axis_tready;
   reg                        m_axis_tready;
   wire [{{i_bits - 1}}:0]    i;
   wire [{{q_bits - 1}}:0]    q;
   wire                       s_axis_tvalid;
   integer                    freq_shift_input;
   integer                    freq_shift_output;

   initial begin
      clk = 1'b0;
      m_axis_tvalid = 1'b0;
      freq_shift_input = $fopen("{{ freq_shift_input }}", "r");
      if (freq_shift_input == `NULL) begin
         $display("freq_shift_input handle was NULL");
      end
      freq_shift_output = $fopen("{{ freq_shift_output }}");
      if (freq_shift_output == `NULL) begin
         $display("freq_shift_output handle was NULL");
      end
   end

   always begin
      #10 clk = ~clk;
   end

   {% include "freq_shift_inst.v" %}
endmodule // freq_shift_tb

