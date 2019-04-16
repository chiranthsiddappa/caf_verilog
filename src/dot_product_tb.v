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
   reg [({{ xi_bits }} * {{ length }}) - 1:0] xi;
   reg [({{ xq_bits }} * {{ length }}) - 1:0] xq;
   reg                                        m_axis_y_tvalid;
   reg [({{ yi_bits }} * {{ length }}) - 1:0] yi;
   reg [({{ yq_bits }} * {{ length }}) - 1:0] yq;
   wire                                       s_axis_product_tvalid;
   wire [{{ sum_i_size }} - 1:0]              i;
   wire [{{ sum_q_size }} - 1:0]              q;
   reg signed [{{ xi_bits - 1}}:0]            xi_in;
   reg signed [{{ xq_bits - 1}}:0]            xq_in;
   reg signed [{{ yi_bits - 1}}:0]            yi_in;
   reg signed [{{ yq_bits - 1}}:0]            yq_in;

   initial begin
      clk = 1'b0;
      m_axis_x_tvalid = 1'b0;
      m_axis_y_tvalid = 1'b0;
      xi = 'd0;
      xq = 'd0;
      yi = 'd0;
      yq = 'd0;
      dot_prod_input = $fopen("{{ dot_prod_input }}", "r");
      scan_counter = 'd0;
      if (dot_prod_input == `NULL) begin
         $display("dot_prod_input was NULL");
         $finish;
      end
      // TODO : write output to a file
   end

   {% include "dot_prod_inst.v" %}

     always begin
        #10 clk = ~clk;
     end

   always @(posedge clk) begin
      if (!$feof(dot_prod_input)) begin
         scan_counter = scan_counter + 1;
         scan_file = $fscanf(dot_prod_input, "%d,%d,%d,%d\n", xi_in,xq_in,yi_in,yq_in);
         xi = (xi << {{ xi_bits }}) | xi_in;
         xq = (xq << {{ xq_bits }}) | xq_in;
         yi = (yi << {{ yi_bits }}) | yi_in;
         yq = (yq << {{ yq_bits }}) | yq_in;
      end
      if (scan_counter > {{ length }}) begin
         m_axis_x_tvalid = 1'b1;
         m_axis_y_tvalid = 1'b1;
         m_axis_product_tready = 1'b1;
      end
      else begin
         m_axis_x_tvalid = 1'b0;
         m_axis_y_tvalid = 1'b0;
      end
   end
endmodule // dot_prod_tb
