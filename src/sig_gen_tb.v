`timescale 1ns/1ns
`define NULL 0

module sig_gen_tb();
   reg clk;
   integer sig_gen_output;

   reg     m_axis_freq_step_tvalid;
   reg [{{phase_bits}}-1: 0] freq_step;
   reg                       m_axis_data_tready;
   wire signed [{{n_bits}}-1:0] cosine;
   wire signed [{{n_bits}}-1:0] sine;
   wire                         s_axis_data_tvalid;
   integer                      icounter;

   initial begin
      clk = 1'b0;
      freq_step = {{ freq_step_str }};
      m_axis_data_tready = 1'b0;
      m_axis_freq_step_tvalid = 1'b0;
      icounter = 'd0;
      sig_gen_output = $fopen("{{ sig_gen_output }}");
      if (sig_gen_output == `NULL) begin
         $display("sig_gen_output handle was NULL");
         $finish;
      end

      @(posedge clk) begin
         m_axis_data_tready = 1'b1;
         m_axis_freq_step_tvalid = 1'b1;
      end

   end // initial begin


   {% include "sig_gen_inst.v" %}
   
   always begin
      #10 clk = ~clk;
   end

   always @(posedge clk) begin
      if (s_axis_data_tvalid & m_axis_data_tready) begin
         $fwrite(sig_gen_output, "%d,%d\n", cosine, sine);
         icounter = icounter + 1'b1;
         if (icounter == 50000) begin
            $fclose(sig_gen_output);
            $finish;
         end
      end
   end
endmodule // sig_gen_tb
