`timescale 1ns/1ns
`define NULL 0

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
   wire [{{ length_counter_bits }}:0] index;
   wire                                   s_axis_tvalid;
   integer                                x_corr_input;
   integer                                counter;

   initial begin
      clk = 1'b0;
      m_axis_tvalid = 1'b0;
      m_axis_tready = 1'b0;
      counter = 'd0;
      x_corr_input = $fopen("{{ x_corr_input_filename }}", "r");
      if (x_corr_input == `NULL) begin
         $display("x_corr_input was NULL");
         $finish;
      end
      @(posedge clk) begin
         m_axis_tready = 1'b1;
      end
      @(posedge s_axis_tvalid);
      @(posedge clk) begin
         m_axis_tready = 1'b0;
      end // UNMATCHED !!
      @(posedge clk) begin
         $finish;
      end      
   end

   always begin
      #10 clk = ~clk;
   end
   
   {% include "x_corr_inst.v" %}

     always @(posedge clk) begin
        if (!$feof(x_corr_input)) begin
           $fscanf(x_corr_input, "%d,%d,%d,%d\n", xi, xq, yi, yq);
           m_axis_tvalid = 1'b1;
           counter = counter + 1'b1;
        end else begin
           m_axis_tvalid = 1'b0;
        end
     end

endmodule // x_corr_tb
