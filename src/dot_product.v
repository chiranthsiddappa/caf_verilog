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
    input [(xi_bits * length) - 1:0] xi,
    input [(xq_bits * length) - 1:0] xq,
    input                                   m_axis_y_tvalid,
    input [(yi_bits * length) - 1:0] yi,
    input [(yq_bits * length) - 1:0] yq,
    output reg                              s_axis_product_tvalid,
    output reg [i_bits-1:0]                 i,
    output reg [q_bits-1:0]                 q
    );

   wire [0:length - 1]                      mult_valid;
   wire signed [xi_bits + yi_bits -1:0]                 mult_out_i [0:length-1];
   wire signed [xi_bits + yi_bits -1:0]                 mult_out_q [0:length-1];
   wire                                     m_axis_data_tvalid;
   genvar                                   iLen;
   integer                                  ithSum;
   reg signed [sum_i_size - 1:0]            sum_i;
   reg signed [sum_q_size - 1:0]            sum_q;

   initial begin
      s_axis_product_tvalid = 1'b0;
   end

   generate
      for (iLen = 0; iLen < length; iLen = iLen + 1) begin: mult_gen

         cpx_multiply #(.xi_bits(xi_bits),
                        .xq_bits(xq_bits),
                        .yi_bits(yi_bits),
                        .yq_bits(yq_bits),
                        .i_bits(xi_bits + yi_bits),
                        .q_bits(xq_bits + yq_bits)) cpx_multiply_dp(.clk(clk),
                                                                    .m_axis_tready(m_axis_product_tready),
                                                                    .m_axis_tvalid(m_axis_data_tvalid),
                                                                    .xi(xi[xi_bits * iLen + xi_bits - 1:xi_bits * iLen]),
                                                                    .xq(xq[xq_bits * iLen + xq_bits - 1:xq_bits * iLen]),
                                                                    .yi(yi[yi_bits * iLen + yi_bits - 1:yi_bits * iLen]),
                                                                    .yq(yq[yq_bits * iLen + yq_bits - 1:yq_bits * iLen]),
                                                                    .s_axis_tvalid(mult_valid[iLen]),
                                                                    .i(mult_out_i[iLen]),
                                                                    .q(mult_out_q[iLen])
                                                                    );
      end
   endgenerate

   assign m_axis_data_tvalid = m_axis_x_tvalid & m_axis_y_tvalid;

   always @(posedge clk) begin
      if (m_axis_product_tready & mult_valid) begin
         for (ithSum = 0, sum_i = 0, sum_q = 0; ithSum < length; ithSum = ithSum + 1) begin
            sum_i = sum_i + mult_out_i[ithSum];
            sum_q = sum_q + mult_out_q[ithSum];
         end
         i <= sum_i;
         q <= sum_q;
         s_axis_product_tvalid <= 1'b1;
      end // if (m_axis_product_tready & mult_valid)
      else begin
         s_axis_product_tvalid <= 1'b0;
      end // else: !if(m_axis_product_tready & mult_valid)
   end
endmodule // dot_prod
