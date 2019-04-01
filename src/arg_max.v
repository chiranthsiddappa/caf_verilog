`timescale 1ns/1ns

module argmax #(parameter buffer_length = 10,
                parameter index_bits = 4,
                parameter out_max_bits=4,
                parameter i_bits = 12,
                parameter q_bits = 12
                )
   (input clk,
    input                                m_axis_tvalid,
    input signed [i_bits - 1:0]          xi,
    input signed [q_bits - 1:0]          xq,
    output reg                           s_axis_tready,
    input                                m_axis_tready,
    output reg [out_max_bits - 1:0] out_max,
    output reg [index_bits - 1:0]        index,
    output reg                           s_axis_tvalid
    );

   reg [index_bits:0]                    icounter;
   reg [i_bits:0]                        i_square;
   reg [q_bits:0]                        q_square;
   reg [i_bits + q_bits - 1:0]           argsum;

   initial begin
      index = 0;
      s_axis_tready = 1'b1;
   end

   always @(posedge clk) begin
      s_axis_tready <= m_axis_tready;
   end

   always @(posedge clk) begin
      if (m_axis_tvalid & s_axis_tready) begin
         if (icounter < buffer_length) begin
            icounter <= icounter + 1'b1;
            s_axis_tvalid <= 1'b0;
         end else begin
            icounter <= 'd0;
            s_axis_tvalid <= 1'b1;
         end
      end
   end // always @ (posedge clk)

   always @(posedge clk) begin
      if (m_axis_tvalid & s_axis_tready) begin
         i_square <= xi * xi;
         q_square <= xq * xq;
         argsum <= (i_square >> 1) + (q_square >> 1);
      end
   end
endmodule // argmax
