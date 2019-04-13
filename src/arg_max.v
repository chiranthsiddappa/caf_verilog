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
   reg [1:0]                        pipeline;

   initial begin
      index = 'd0;
      s_axis_tready = 1'b1;
      icounter = 'd0;
      out_max = 'd0;
      s_axis_tvalid = 1'b0;
      pipeline = 2'b0;
   end

   always @(posedge clk) begin
      if (icounter < buffer_length) begin
         s_axis_tready <= 1'b1;
      end else begin
         s_axis_tready <= 1'b0;
      end
   end

   always @(posedge clk) begin
      if (m_axis_tvalid & s_axis_tready) begin
         if (icounter < buffer_length) begin
            icounter <= icounter + 1'b1;
         end
      end else if(m_axis_tready) begin
         if ((icounter > buffer_length - 1) && (icounter <= buffer_length)) begin
            icounter <= icounter + 1'b1;
         end else if (icounter == buffer_length + 1)  begin
            icounter <= 'd0;
         end
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

   always @(posedge clk) begin
      if ((icounter <= buffer_length + 1'b1) & m_axis_tready) begin
         argsum <= (i_square >> i_bits-1) + (q_square >> q_bits-1);
      end
   end

   always @(posedge clk) begin
      if (icounter < 'd1) begin
         out_max <= 'd0;
         index <= 'd0;
      end else begin
         if (argsum > out_max) begin
            if (icounter >= buffer_length) begin
               index <= buffer_length - 1;
            end
            else begin
               index <= icounter - (pipeline[1] + pipeline[0]);
            end
            out_max <= argsum;
         end
      end
      pipeline <= (pipeline << 1) | m_axis_tvalid;
   end // always @ (posedge clk)

   always @(posedge clk) begin
      if ((icounter == buffer_length + 1)) begin
         s_axis_tvalid <= 1'b1;
      end else begin
         s_axis_tvalid <= 1'b0;
      end
   end
endmodule // argmax
