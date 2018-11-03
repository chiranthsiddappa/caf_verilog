`timescale 1ns/1ns
`define NULL 0

module cpx_multiply_tb();
   reg clk;
   integer               cpx_multiply_input; // file handler
   integer               scan_file; // file handler
   integer               cpx_multiply_output;

   reg                   m_axis_x_tvalid;
   reg signed [{{ xi_bits - 1 }}:0] xi;
   reg signed [{{ xq_bits - 1 }}:0] xq;
   reg                              m_axis_y_tvalid;
   reg signed [{{ yi_bits - 1 }}:0] yi;
   reg signed [{{ yq_bits - 1 }}:0] yq;
   wire                             s_axis_i_tvalid;
   wire signed [{{ i_out_bits - 1 }}:0] i_out;
   wire                                 s_axis_q_tvalid;
   wire signed [{{ q_out_bits - 1 }}:0] q_out;

   initial begin
      clk = 1'b0;
      m_axis_x_tvalid = 1'b0;
      m_axis_y_tvalid = 1'b0;
      cpx_multiply_input = $fopen("{{ cpx_multiply_input }}", "r");
      if (cpx_multiply_input == `NULL) begin
         $display("cpx_multiply_input handle was NULL");
         $finish;
      end
      cpx_multiply_output = $fopen("{{ cpx_multiply_output }}");
      if (cpx_multiply_output == `NULL) begin
         $display("cpx_multiply_output handle was NULL");
         $finish;
      end
      #10
        m_axis_x_tvalid = 1'b1;
      m_axis_y_tvalid = 1'b1;
   end

   always begin
      #10 clk = ~clk;
   end

   {% include "cpx_multiply_inst.v" %}

   always @(posedge clk) begin
      scan_file = $fscanf(cpx_multiply_input, "%d,%d,%d,%d\n", xi,xq,yi,yq);
      if (s_axis_i_tvalid & s_axis_q_tvalid) begin
         $fwrite(cpx_multiply_output, "%d,%d\n", i_out,q_out);
      end
      if ($feof(cpx_multiply_input)) begin
         $finish;
      end
   end
endmodule // cpx_multiply_tb
