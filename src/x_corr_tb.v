`timescale 1ns/1ns

module x_corr_tb();
   reg clk;
   wire s_axis_tready;
   reg [{{ xi_bits - 1 }}:0] xi;
   reg [{{ xq_bits - 1 }}:0] xq;
   reg [{{ yi_bits - 1 }}:0] yi;
   reg [{{ yq_bits - 1 }}:0] yq;
   reg                       m_axis_tvalid;
   reg                       m_axis_tready;
   wire [{{ out_max_bits - 1 }}:0] out_max;
   wire [{{ length_counter_bits - 1 }}:0] index;
   wire                                   s_axis_tvalid;


   initial begin
      clk = 1'b0;
   end

   always begin
      #10 clk = ~clk;
   end
   
   {% include "x_corr_inst.v" %}
     
     endmodule // x_corr_tb
