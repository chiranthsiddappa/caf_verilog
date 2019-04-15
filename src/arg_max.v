`timescale 1ns/1ns

module argmax #(parameter buffer_length = 10,
                parameter index_bits = 4,
                parameter out_max_bits = 4,
                parameter i_bits = 12,
                parameter q_bits = 12
                )
   (input clk,
    input                           m_axis_tvalid,
    input signed [i_bits - 1:0]     xi,
    input signed [q_bits - 1:0]     xq,
    output reg                      s_axis_tready,
    input                           m_axis_tready,
    output reg [out_max_bits - 1:0] out_max,
    output reg [index_bits - 1:0]   index,
    output reg                      s_axis_tvalid
    );

   reg [index_bits:0]               icounter;
   reg [i_bits + i_bits - 2:0]      i_square;
   reg [q_bits + q_bits - 2:0]      q_square;
   reg [out_max_bits - 1:0]         argsum;
   reg [out_max_bits - 1:0]         out_max_buff;
   
   initial begin
      out_max_buff = 'd0;
      index = 'd0;
      s_axis_tready = 1'b1;
      icounter = 'd0;
      out_max = 'd0;
      s_axis_tvalid = 1'b0;
      argsum = 'd0;
   end

   always @(posedge clk) begin
      if (icounter < buffer_length - 1) begin
         s_axis_tready <= 1'b1;
      end else if ((icounter == buffer_length - 1) && m_axis_tvalid) begin
         s_axis_tready <= 1'b0;
      end
   end

   always @(posedge clk) begin
      if (icounter < buffer_length) begin
         if (m_axis_tvalid && s_axis_tready) begin
            icounter <= icounter + 1'b1;
         end
      end
      else if (icounter >= buffer_length && m_axis_tready) begin
         icounter <= 'd0;
      end
      else if (!s_axis_tvalid) begin
         icounter <= icounter + 1'b1;
      end
   end // always @ (posedge clk)

   always @(posedge clk) begin
      if (m_axis_tvalid & s_axis_tready) begin
         i_square <= xi * xi;
         q_square <= xq * xq;
      end else begin
         i_square <= i_square;
         q_square <= q_square;
      end
   end

   always @(i_square or q_square) begin
      argsum <= (i_square >> i_bits-1) + (q_square >> q_bits-1);
   end

   always @(icounter or argsum) begin
      if (icounter == 'd0) begin
         out_max_buff <= 'd0;
      end
      else if (argsum > out_max_buff) begin
         out_max_buff <= argsum;
         index <= icounter - 1'b1;
      end
   end

   always @(posedge clk) begin
      if (icounter == buffer_length) begin
         s_axis_tvalid <= 1'b1;
         out_max <= out_max_buff;
      end else begin
         s_axis_tvalid <= 1'b0;
      end
   end
endmodule // argmax
