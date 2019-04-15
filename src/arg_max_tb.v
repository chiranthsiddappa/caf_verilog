`timescale 1ns/1ns
`define NULL 0

module argmax_tb();
   reg clk;
   reg signed [{{i_bits - 1}}:0] xi;
   reg signed [{{q_bits - 1}}:0] xq;
   integer                       arg_max_input;
   reg                           m_axis_tvalid;
   wire                          s_axis_tready;
   reg                           m_axis_tready;
   wire [{{ out_max_bits - 1}}:0]   out_max;
   wire [{{ index_bits }}:0]   index;
   wire                          s_axis_tvalid;

   initial begin
      clk = 1'b0;
      m_axis_tready = 1'b1;
      m_axis_tvalid = 1'b0;
      arg_max_input = $fopen("{{ arg_max_input }}", "r");
      if (arg_max_input == `NULL) begin
         $display("arg_max_input handle was NULL");
         $finish;
      end
      @(posedge s_axis_tvalid);
      @(posedge clk) begin
         m_axis_tready = 1'b0;
      end // UNMATCHED !!
      @(posedge clk);
      @(posedge clk);
      $finish;
   end

   always begin
      #10 clk = ~clk;
   end

   {% include "arg_max_inst.v" %}

     always @(posedge clk) begin
        $fscanf(arg_max_input, "%d,%d\n", xi, xq);
        m_axis_tvalid = 1'b1;
        if ($feof(arg_max_input)) begin
           m_axis_tvalid = 1'b0;
        end
     end
endmodule // argmax_tb
