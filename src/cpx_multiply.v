`timescale 1ns/1ns

module cpx_multiply #(parameter xi_bits = 12,
		      parameter xq_bits = 12,
		      parameter yi_bits = 12,
		      parameter yq_bits = 12,
		      parameter i_bits = 24,
		      parameter q_bits = 24
		      )
   (input clk,
    input                          m_axis_tready,
    input                          m_axis_tvalid,
    input signed [xi_bits-1:0]     xi,
    input signed [xq_bits-1:0]     xq,
    input signed [yi_bits-1:0]     yi,
    input signed [yq_bits-1:0]     yq,
    output reg s_axis_tready,
    output reg signed [i_bits-1:0] i,
    output reg signed [q_bits-1:0] q,
    output reg                     s_axis_tvalid
    );

   reg [3:0]                       pipeline;

   initial begin
      pipeline = 5'b0;
      s_axis_tready = 1'b0;
      s_axis_tvalid = 1'b0;
   end

   /**
    * Represent each step of:
    *    x       y
    * (x + yi)(u + vi) = (xu - yv) + (xv + yu)i
    */
   reg signed [xi_bits + yi_bits:0] 	   i_sub;
   reg signed [xi_bits + yi_bits - 1:0]    i_sub_out;
   reg signed [xq_bits + yq_bits:0] 	   q_add;
   reg signed [xq_bits + yq_bits - 1:0]    q_add_out;
   reg signed [xi_bits + yi_bits:0] 	   xu;
   reg signed [xi_bits + yi_bits:0]        xu_out;
   reg signed [xq_bits + yq_bits:0] 	   yv;
   reg signed [xq_bits + yq_bits:0]        yv_out;
   reg signed [xi_bits + yq_bits:0] 	   xv;
   reg signed [xi_bits + yq_bits:0]        xv_out;
   reg signed [xq_bits + yi_bits:0] 	   yu;
   reg signed [xq_bits + yi_bits:0]        yu_out;

   always @(posedge clk) begin
      if (m_axis_tvalid & s_axis_tready) begin
         xu <= xi * yi;
         yv <= xq * yq;
         xv <= xi * yq;
         yu <= xq * yi;
      end else begin
         xu <= xu;
         yv <= yv;
         xv <= xv;
         yu <= yu;
      end // else: !if(m_axis_tvalid & s_axis_tready)
   end

   always @(posedge clk) begin
      if(m_axis_tready) begin
         xu_out <= xu;
         yv_out <= yv;
         xv_out <= xv;
         yu_out <= yu;
         i_sub <= xu_out - yv_out;
         i_sub_out <= i_sub;
         q_add <= xv_out + yu_out;
         q_add_out <= q_add;
      end // if (m_axis_tvalid)
      else begin
         xu_out <= xu_out;
         yv_out <= yv_out;
         xv <= xv;
         xv_out <= xv_out;
         yu <= yu;
         yu_out <= yu_out;
         i_sub <= i_sub;
         i_sub_out <= i_sub_out;
         q_add <= q_add;
         q_add_out <= q_add_out;
      end // else: !if(m_axis_tvalid)
      i <= i_sub_out[xi_bits+yi_bits-1: xi_bits+yi_bits-i_bits];
      q <= q_add_out[xq_bits+yq_bits-1: xq_bits+yq_bits-q_bits];
   end // always @ (posedge clk)

   always @(posedge clk) begin
      if(m_axis_tvalid & s_axis_tready) begin
         pipeline <= (pipeline << 1) | m_axis_tready;
      end else if (m_axis_tready) begin
         pipeline <= (pipeline << 1);
      end
      s_axis_tvalid <= pipeline[3];
   end // always @ (posedge clk)

   always @(posedge clk) begin
      s_axis_tready <= m_axis_tready | ~pipeline[0];
   end

endmodule // cpx_multiply
