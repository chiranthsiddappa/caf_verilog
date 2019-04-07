`timescale 1ns/1ns
`define NULL 0

module dot_prod_pip_tb();
   reg clk;
   integer dot_prod_pip_input;
   integer scan_file;
   integer scan_counter;
   reg     m_axis_product_tready;
   reg     m_axis_x_tvalid;
   reg [{{ xi_bits - 1 }}:0] xi;
   reg [{{ xq_bits - 1 }}:0] xq;
   reg                                        m_axis_y_tvalid;
   reg [{{ yi_bits - 1 }}:0] yi;
   reg [{{ yq_bits - 1 }}:0] yq;
   wire                                       s_axis_product_tvalid;
   wire [{{ sum_i_bits - 1 }}:0]              i;
   wire [{{ sum_q_bits - 1 }}:0]              q;
   reg signed [{{ xi_bits - 1 }}:0]            xi_in;
   reg signed [{{ xq_bits - 1 }}:0]            xq_in;
   reg signed [{{ yi_bits - 1 }}:0]            yi_in;
   reg signed [{{ yq_bits - 1 }}:0]            yq_in;

   initial begin
      clk = 1'b0;
      m_axis_x_tvalid = 1'b0;
      m_axis_y_tvalid = 1'b0;
      xi = 'd0;
      xq = 'd0;
      yi = 'd0;
      yq = 'd0;
      dot_prod_pip_input = $fopen("{{ dot_prod_input }}", "r");
      scan_counter = 'd0;
      if (dot_prod_pip_input == `NULL) begin
         $display("dot_prod_input was NULL");
         $finish;
      end
      @(posedge s_axis_product_tvalid);
      @(posedge clk) begin
                  m_axis_product_tready = 1'b0;
      end
      @(posedge clk) begin
         $finish;
      end // UNMATCHED !!
   end // initial begin

   {% include "dot_prod_pip_inst.v" %}

     always begin
        #10 clk = ~clk;
     end

   always @(posedge clk) begin
      if (!$feof(dot_prod_pip_input)) begin
         scan_counter = scan_counter + 1;
         scan_file = $fscanf(dot_prod_pip_input, "%d,%d,%d,%d\n", xi_in, xq_in, yi_in, yq_in);
         xi = xi_in;
         xq = xq_in;
         yi = yi_in;
         yq = yq_in;
      end
      if (scan_counter <= {{ length }}) begin
         m_axis_x_tvalid = 1'b1;
         m_axis_y_tvalid = 1'b1;
         m_axis_product_tready = 1'b1;
      end
      else begin
         m_axis_x_tvalid = 1'b0;
         m_axis_y_tvalid = 1'b0;
      end
   end // always @ (posedge clk)
endmodule // dot_prod_pip_tb
