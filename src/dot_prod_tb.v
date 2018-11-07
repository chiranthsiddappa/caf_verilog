`timescale 1ns/1ns
`define NULL 0


module dot_prod_tb();
   reg clk;
   integer dot_prod_input;
   integer scan_file;
   integer scan_counter;
   integer dot_prod_output;
   reg     m_axis_product_tready;
   reg     m_axis_x_tvalid;
   reg signed [({{ xi_bits }} * {{ length }}) - 1:0] xi;
   reg signed [({{ xq_bits }} * {{ length }}) - 1:0] xq;
   reg                                               m_axis_y_tvalid;
   reg signed [({{ yi_bits }} * {{ length }}) - 1:0] yi;
   reg signed [({{ yq_bits }} * {{ length }}) - 1:0] yq;
   wire                                              s_axis_tvalid;
   wire [{{ sum_i_size }} - 1:0]                     i;
   wire [{{ sum_q_size }} - 1:0]                     q;
   reg signed [{{ xi_bits - 1}}:0]                   xi_in;
   reg signed [{{ xq_bits - 1}}:0]                   xq_in;
   reg signed [{{ yi_bits - 1}}:0]                   yi_in;
   reg signed [{{ yq_bits - 1}}:0]                   yq_in;

   initial begin
      clk = 1'b0;
      m_axis_x_tvalid = 1'b0;
      m_axis_y_tvalid = 1'b0;
      dot_prod_input = $fopen("{{ dot_prod_input }}", "r");
      if (dot_prod_input == `NULL) begin
         $display("dot_prod_input was NULL");
         $finish;
      end
      for (scan_counter = 0; !$feof(dot_prod_input); scan_counter = scan_counter + 1) begin
         scan_file = $fscanf(dot_prod_input, "%d,%d,%d,%d\n", xi_in,xq_in,yi_in,yq_in);
         
      end
      // TODO : write output to a file
      #10
        m_axis_x_tvalid = 1'b1;
      m_axis_y_tvalid = 1'b1;
   end

   {% include "dot_prod_inst.v" %}
   
   always begin
      #10 clk = ~clk;
   end

   always @(posedge clk) begin

   end
endmodule // dot_prod_tb
