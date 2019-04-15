`timescale 1ns/1ns
`define NULL 0

module freq_shift_tb();
   reg clk;
   reg m_axis_tvalid;
   reg [{{freq_shift_phase_bits - 1}}:0] freq_step;
   reg                        neg_shift;
   reg [{{freq_shift_i_bits - 1}}:0]     xi;
   reg [{{freq_shift_q_bits - 1}}:0]     xq;
   wire                       s_axis_tready;
   reg                        m_axis_tready;
   wire signed [{{freq_shift_i_bits - 1}}:0]    i;
   wire signed [{{freq_shift_q_bits - 1}}:0]    q;
   wire                       s_axis_tvalid;
   integer                    freq_shift_input;
   integer                    freq_shift_output;

   initial begin
      clk = 1'b0;
      m_axis_tvalid = 1'b0;
      m_axis_tready = 1'b0;
      freq_step = {{ freq_step_str }};
      neg_shift = {{ neg_shift_str }};
      freq_shift_input = $fopen("{{ freq_shift_input }}", "r");
      if (freq_shift_input == `NULL) begin
         $display("freq_shift_input handle was NULL");
      end
      freq_shift_output = $fopen("{{ freq_shift_output }}");
      if (freq_shift_output == `NULL) begin
         $display("freq_shift_output handle was NULL");
      end
      @(posedge clk) begin
         $fscanf(freq_shift_input, "%d,%d\n", xi,xq);
         m_axis_tvalid = 1'b1;
      end
      @(negedge s_axis_tvalid) begin
         $fclose(freq_shift_output);
         $finish;
      end
   end

   always begin
      #10 clk = ~clk;
   end

   {% include "freq_shift_inst.v" %}

     always @(posedge clk) begin
        if (s_axis_tready) begin
           $fscanf(freq_shift_input, "%d,%d\n", xi,xq);
           m_axis_tvalid = 1'b1;
           m_axis_tready = 1'b1;
        end
        if ($feof(freq_shift_input)) begin
           m_axis_tvalid = 1'b0;
        end
     end

   always @(posedge clk) begin
      if (s_axis_tvalid) begin
         $fwrite(freq_shift_output, "%d,%d\n", i, q);
      end
   end
endmodule // freq_shift_tb
