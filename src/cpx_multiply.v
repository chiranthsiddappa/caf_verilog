`timescale 1ns/1ns

module cpx_multiply #(parameter xi_bits = 12,
		      parameter xq_bits = 12,
		      parameter yi_bits = 12,
		      parameter yq_bits = 12,
		      parameter i_bits = 24,
		      parameter q_bits = 24
		      )
   (input clk,
    input                          m_axis_x_tvalid,
    input signed [xi_bits-1:0]     xi,
    input signed [xq_bits-1:0]     xq,
    input                          m_axis_y_tvalid,
    input signed [yi_bits-1:0]     yi,
    input signed [yq_bits-1:0]     yq,
    output reg                     s_axis_i_tvalid,
    output reg signed [i_bits-1:0] i,
    output reg                     s_axis_q_tvalid,
    output reg signed [q_bits-1:0] q
    );

   reg [3:0]                       pipeline;

   initial begin
      pipeline = 5'b0;
   end

   /**
    * Represent each step of:
    *    x       y
    * (x + yi)(u + vi) = (xu - yv) + (xv + yu)i
    */
   reg signed [xi_bits + yi_bits:0] 	   i_sub;
   reg signed [xi_bits + yi_bits:0]        i_sub_out;
   reg signed [xq_bits + yq_bits:0] 	   q_add;
   reg signed [xq_bits + yq_bits:0]        q_add_out;
   reg signed [xi_bits + yi_bits:0] 	   xu;
   reg signed [xi_bits + yi_bits:0]        xu_out;
   reg signed [xq_bits + yq_bits:0] 	   yv;
   reg signed [xq_bits + yq_bits:0]        yv_out;
   reg signed [xi_bits + yq_bits:0] 	   xv;
   reg signed [xi_bits + yq_bits:0]        xv_out;
   reg signed [xq_bits + yi_bits:0] 	   yu;
   reg signed [xq_bits + yi_bits:0]        yu_out;
   wire                                    in_valid;

   assign in_valid = m_axis_x_tvalid & m_axis_y_tvalid;

   always @(posedge clk) begin
      if(in_valid) begin
         xu <= xi * yi;
         xu_out <= xu;
         yv <= xq * yq;
         yv_out <= yv;
         xv <= xi * yq;
         xv_out <= xv;
         yu <= xq * yi;
         yu_out <= yu;
         i_sub <= xu_out - yv_out;
         i_sub_out <= i_sub;
         q_add <= xv_out + yu_out;
         q_add_out <= q_add;
      end // if (in_valid)
      else begin
         xu <= xu;
         xu_out <= xu_out;
         yv <= yv;
         yv_out <= yv_out;
         xv <= xv;
         xv_out <= xv_out;
         yu <= yu;
         yu_out <= yu_out;
         i_sub <= i_sub;
         i_sub_out <= i_sub_out;
         q_add <= q_add;
         q_add_out <= q_add_out;
      end // else: !if(in_valid)
      i <= i_sub_out[i_bits:0];
      q <= q_add_out[q_bits:0];
   end // always @ (posedge clk)

   always @(posedge clk) begin
      if(in_valid) begin
         pipeline <= (pipeline << 1) | 4'b1;
         s_axis_i_tvalid <= pipeline[3];
         s_axis_q_tvalid <= pipeline[3];
      end
   end // always @ (posedge clk)

endmodule // cpx_multiply
