`timescale 1ns/1ns

module cpx_multiply #(parameter xi_bits = 12,
		      parameter xq_bits = 12,
		      parameter yi_bits = 12,
		      parameter yq_bits = 12,
		      parameter i_bits = 24,
		      parameter q_bits = 24
		      )
   (input clk,
    input signed [xi_bits-1:0] 	  xi,
    input signed [xq_bits-1:0] 	  xq,
    input signed [yi_bits-1:0] 	  yi,
    input signed [yq_bits-1:0] 	  yq,
    output reg signed [i_bits-1:0] i,
    output reg signed [q_bits-1:0] q
    );

   /**
    * Represent each step of:
    *    x       y
    * (x + yi)(u + vi) = (xu - yv) + (xv + yu)i
    */
   reg signed [xi_bits + yi_bits:0] 	   i_sub;
   reg signed [xq_bits + yq_bits:0] 	   q_add;
   reg signed [xi_bits + yi_bits:0] 	   xu;
   reg signed [xq_bits + yq_bits:0] 	   yv;
   reg signed [xi_bits + yq_bits:0] 	   xv;
   reg signed [xq_bits + yi_bits:0] 	   yu;

   always @(posedge clk) begin
      xu <= xi * yi;
      yv <= xq * yq;
      xv <= xi * yq;
      yu <= xq * yi;
      i_sub <= xu - yv;
      q_add <= xv + yu;
      i <= i_sub[i_bits:0];
      q <= q_add[q_bits:0];
   end

endmodule // cpx_multiply
