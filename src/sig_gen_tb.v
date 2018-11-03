`timescale 1ns/1ns
`define NULL 0

module sig_gen_tb();
   reg clk;
   integer sig_gen_output;

   reg [{{phase_bits}}-1: 0] freq_step;
   reg                       m_axis_data_tready;
   wire signed [{{n_bits}}-1:0] cosine;
   wire signed [{{n_bits}}-1:0] sine;
   wire                         s_axis_data_tvalid;

   initial begin
      clk = 1'b0;
      freq_step = {{ freq_step_str }};
      m_axis_data_tready = 1'b0;
      sig_gen_output = $fopen("{{ sig_gen_output }}");
      if (sig_gen_output == `NULL) begin
         $display("sig_gen_output handle was NULL");
         $finish;
      end

      @(posedge clk) m_axis_data_tready = 1'b1;

   end // initial begin


   {% include "sig_gen_inst.v" %}
   
   always begin
      #10 clk = ~clk;
   end

   always @(posedge clk) begin
      if (s_axis_data_tvalid) begin
         $fwrite(sig_gen_output, "%d,%d\n", cosine, sine);
      end
   end
endmodule // sig_gen_tb