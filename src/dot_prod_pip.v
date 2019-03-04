`timescale 1ns/1ns

module dot_prod_pip #(parameter xi_bits = 12,
                      parameter xq_bits = 12,
                      parameter yi_bits = 12,
                      parameter yq_bits = 12,
                      parameter i_bits = 24,
                      parameter q_bits = 24,
                      parameter length = 5,
                      parameter length_counter_size = 3,
                      parameter sum_i_size = 24,
                      parameter sum_q_size = 24
                      )
   (input clk,
    input                            m_axis_product_tready,
    input                            m_axis_x_tvalid,
    input [xi_bits - 1:0] xi,
    input [xq_bits - 1:0] xq,
    input                            m_axis_y_tvalid,
    input [yi_bits - 1:0] yi,
    input [yq_bits - 1:0] yq,
    output reg                       s_axis_product_tvalid,
    output reg [i_bits-1:0]          i,
    output reg [q_bits-1:0]          q
    );

   wire signed [xi_bits + yi_bits -1:0] mult_out_i;
   wire signed [xi_bits + yi_bits -1:0] mult_out_q;
   wire                                 m_axis_data_tvalid;
   reg signed [sum_i_size - 1:0]        sum_i;
   reg signed [sum_q_size - 1:0]        sum_q;
   reg [length_counter_size:0]          length_counter;
   wire                                 s_axis_cpx_i_tvalid;
   wire                                 s_axis_cpx_q_tvalid;
   wire                                 s_axis_cpx_product_tvalid;

   initial begin
      s_axis_product_tvalid = 1'b0;
      length_counter = 'd0;
      sum_i = 'd0;
      sum_q = 'd0;
   end

   cpx_multiply #(.xi_bits(xi_bits),
                  .xq_bits(xq_bits),
                  .yi_bits(yi_bits),
                  .yq_bits(yq_bits),
                  .i_bits(xi_bits + yi_bits),
                  .q_bits(xq_bits + yq_bits)) cpx_multiply_dot_pip(.clk(clk),
                                                               .m_axis_x_tvalid(m_axis_x_tvalid),
                                                               .xi(xi),
                                                               .xq(xq),
                                                               .m_axis_y_tvalid(m_axis_y_tvalid),
                                                               .yi(yi),
                                                               .yq(yq),
                                                               .i(mult_out_i),
                                                                   .s_axis_i_tvalid(s_axis_cpx_i_tvalid),
                                                               .q(mult_out_q),
                                                                   .s_axis_q_tvalid(s_axis_cpx_q_tvalid));

   assign s_axis_cpx_product_tvalid = s_axis_cpx_i_tvalid & s_axis_cpx_q_tvalid;

   always @(posedge clk) begin
      if (s_axis_cpx_product_tvalid && m_axis_product_tready) begin
         if (length_counter < length) begin
            length_counter <= length_counter + 1'b1;
            sum_i <= sum_i + mult_out_i;
            sum_q <= sum_q + mult_out_q;
            s_axis_product_tvalid <= 1'b0;
         end
         else begin
            length_counter <= 'd0;
            sum_i <= 'd0;
            sum_q <= 'd0;
            i <= sum_i;
            q <= sum_q;
            s_axis_product_tvalid <= 1'b1;
         end // else: !if(length_counter < length)
      end // if (s_axis_product_tvalid)
   end // always @ (posedge clk)
endmodule // dot_prod
