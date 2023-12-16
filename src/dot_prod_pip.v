`timescale 1ns/1ns

module dot_prod_pip #(parameter xi_bits = 12,
                      parameter xq_bits = 12,
                      parameter yi_bits = 12,
                      parameter yq_bits = 12,
                      parameter i_bits = 24,
                      parameter q_bits = 24,
                      parameter length = 5,
                      parameter length_counter_bits = 3,
                      parameter sum_i_bits = 24,
                      parameter sum_q_bits = 24
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

   wire                                 cpx_m_axis_tvalid;
   wire signed [xi_bits + yi_bits -1:0] mult_out_i;
   wire signed [xq_bits + yq_bits -1:0] mult_out_q;
   wire signed [sum_i_bits - 1:0]       mult_out_i_extended;
   wire signed [sum_q_bits - 1:0]       mult_out_q_extended;

   wire                                 m_axis_data_tvalid;
   reg signed [sum_i_bits - 1:0]        sum_i;
   reg signed [sum_i_bits - 1:0]        sum_i_rs;
   reg signed [sum_q_bits - 1:0]        sum_q;
   reg signed [sum_q_bits - 1:0]        sum_q_rs;

   reg [length_counter_bits:0]          length_counter;
   wire [31:0]                          length_counter_extended;
   wire                                 s_axis_cpx_tvalid;
   wire                                 s_axis_cpx_tready;

   initial begin
      s_axis_product_tvalid = 1'b0;
      length_counter = -'d1;
      sum_i = 'd0;
      sum_q = 'd0;
   end

   // Internal sign-extensions
   assign cpx_m_axis_tvalid = m_axis_x_tvalid & m_axis_y_tvalid;
   assign mult_out_i_extended = { {(sum_i_bits - (xi_bits + yi_bits)){mult_out_i[xi_bits + yi_bits - 1]}}, mult_out_i};
   assign mult_out_q_extended = { {(sum_q_bits - (xq_bits + yq_bits)){mult_out_q[xq_bits + yq_bits - 1]}}, mult_out_q};
   assign length_counter_extended = { {(31 - length_counter_bits){length_counter[length_counter_bits-1]}}, length_counter};

   cpx_multiply #(.xi_bits(xi_bits),
                  .xq_bits(xq_bits),
                  .yi_bits(yi_bits),
                  .yq_bits(yq_bits),
                  .i_bits(xi_bits + yi_bits),
                  .q_bits(xq_bits + yq_bits)) cpx_multiply_dot_pip(.clk(clk),
                                                                   .m_axis_tready(m_axis_product_tready),
                                                                   .m_axis_tvalid(cpx_m_axis_tvalid),
                                                                   .xi(xi),
                                                                   .xq(xq),
                                                                   .yi(yi),
                                                                   .yq(yq),
                                                                   .i(mult_out_i),
                                                                   .q(mult_out_q),
                                                                   .s_axis_tready(s_axis_cpx_tready),
                                                                   .s_axis_tvalid(s_axis_cpx_tvalid));

   always @(posedge clk) begin
      if (s_axis_cpx_tvalid && m_axis_product_tready) begin
         if (length_counter_extended < length - 1) begin
            length_counter <= length_counter + 1'b1;
            sum_i <= sum_i + mult_out_i_extended;
            sum_q <= sum_q + mult_out_q_extended;
         end
         else begin
            length_counter <= 'd0;
            sum_i <= mult_out_i_extended;
            sum_q <= mult_out_q_extended;
         end // else: !if(length_counter < length)
      end // if (s_axis_product_tvalid)
      else if (m_axis_product_tready) begin
         if(length_counter_extended == length - 1) begin
            length_counter <= 'd0;
            sum_i <= 'd0;
            sum_q <= 'd0;
         end
      end
   end // always @ (posedge clk)

   always @(posedge clk) begin
      if(length_counter_extended == length - 1) begin
         s_axis_product_tvalid <= 1'b1;
         sum_i_rs = sum_i >> (sum_i_bits - i_bits);
         sum_q_rs = sum_q >> (sum_q_bits - q_bits);
         i <= sum_i_rs[sum_i_bits - 1:(sum_i_bits - i_bits)];
         q <= sum_q_rs[sum_i_bits - 1:(sum_q_bits - q_bits)];
      end
      else begin
         s_axis_product_tvalid <= 1'b0;
         i <= i;
         q <= q;
      end
   end
endmodule // dot_prod
