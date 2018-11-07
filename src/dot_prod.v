`timescale 1ns/1ns

module dot_prod #(parameter xi_bits = 12,
		  parameter xq_bits = 12,
		  parameter yi_bits = 12,
		  parameter yq_bits = 12,
                  parameter i_bits = 24,
                  parameter q_bits = 24,
                  parameter length = 5,
                  parameter sum_i_size = 24,
                  parameter sum_q_size = 24
		  )
   (input clk,
    input                                   m_axis_product_tready,
    input                                   m_axis_x_tvalid,
    input signed [(xi_bits * length) - 1:0] xi,
    input signed [(xq_bits * length) - 1:0] xq,
    input                                   m_axis_y_tvalid,
    input signed [(yi_bits * length) - 1:0] yi,
    input signed [(yq_bits * length) - 1:0] yq,
    output reg                              s_axis_tvalid,
    output reg [i_bits-1:0]                 i,
    output reg [q_bits-1:0]                 q
    );

   wire [0:length-1]                        mult_valid_i;
   wire [0:length-1]                        mult_valid_q;
   wire                                     mult_valid;
   wire signed [i_bits-1:0]                 mult_out_i [0:length-1];
   wire signed [q_bits-1:0]                 mult_out_q [0:length-1];
   wire                                     m_axis_data_tvalid;
   genvar                                   iLen;
   integer                                  ithSum;
   reg signed [sum_i_size - 1:0]            sum_i;
   reg signed [sum_q_size - 1:0]            sum_q;

   generate
      for (iLen = 0; iLen < length; iLen = iLen + 1) begin: mult_gen

         cpx_multiply #(.xi_bits(xi_bits),
                        .xq_bits(xq_bits),
                        .yi_bits(yi_bits),
                        .yq_bits(yq_bits),
                        .i_bits(xi_bits + yi_bits),
                        .q_bits(xq_bits + yq_bits)) cpx_multiply_dp(.clk(clk),
                                                                    .m_axis_x_tvalid(m_axis_x_tvalid),
                                                                    .xi(xi[xi_bits * iLen + xi_bits - 1:xi_bits * iLen]),
                                                                    .xq(xq[xq_bits * iLen + xq_bits - 1:xq_bits * iLen]),
                                                                    .m_axis_y_tvalid(m_axis_y_tvalid),
                                                                    .yi(yi[yi_bits * iLen + yi_bits - 1:yi_bits * iLen]),
                                                                    .yq(yq[yq_bits * iLen + yq_bits - 1:yq_bits * iLen]),
                                                                    .s_axis_i_tvalid(mult_valid_i[iLen]),
                                                                    .s_axis_q_tvalid(mult_valid_q[iLen]),
                                                                    .i(mult_out_i[iLen]),
                                                                    .q(mult_out_q[iLen])
                                                                    );
      end
   endgenerate

   assign m_axis_data_tvalid = m_axis_x_tvalid & m_axis_y_tvalid;
   assign mult_valid = (&mult_valid_i) & (&mult_valid_q);

   always @(posedge clk) begin
      if (m_axis_product_tready & mult_valid) begin
         sum_i = 'd0;
         sum_q = 'd0;
         for (ithSum = 0; ithSum < length; ithSum = ithSum + 1) begin
            sum_i = sum_i + mult_out_i[ithSum];
            sum_q = sum_q + mult_out_q[ithSum];
         end
      end
   end
endmodule // dot_prod
