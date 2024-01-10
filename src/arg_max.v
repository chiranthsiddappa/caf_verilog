`timescale 1ns/1ns

module arg_max #(parameter buffer_length = 10,
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
    output reg [index_bits:0]       index,
    output reg                      s_axis_tvalid
    );

   reg [1:0]                           m_axis_tvalid_buff;
   reg [index_bits:0]                  icounter;
   reg [index_bits:0]                  icounter_buff;
   wire [31:0]                         icounter_extended;
   wire [31:0]                         icounter_buff_extended;
   reg [i_bits + i_bits - 2:0]         i_square;
   reg [i_bits + i_bits - 2:0]         i_square_rs;
   reg [q_bits + q_bits - 2:0]         q_square;
   reg [q_bits + q_bits - 2:0]         q_square_rs;
   reg [out_max_bits - 1:0]            argsum;
   reg [out_max_bits - 1:0]            out_max_buff;

   initial begin
      out_max_buff = 'd0;
      index = 'd0;
      s_axis_tready = 1'b0;
      icounter = 'd0;
      out_max = 'd0;
      s_axis_tvalid = 1'b0;
      argsum = 'd0;
   end

   // Buffered timing signals
   always @(posedge clk) begin
      m_axis_tvalid_buff[0] <= m_axis_tvalid;
      m_axis_tvalid_buff[1] <= m_axis_tvalid_buff[0];
      icounter_buff <= icounter;
   end

   assign icounter_extended = { {(31 - index_bits){icounter[index_bits]}}, icounter};
   assign icounter_buff_extended = { {(31 - index_bits){icounter_buff[index_bits]}}, icounter_buff};

   // s_axis_tready block with catch
   always @(posedge clk) begin
      if (icounter_extended < buffer_length) begin
         s_axis_tready <= 1'b1;
      end
      else if (icounter_extended == buffer_length & m_axis_tready) begin
         s_axis_tready <= 1'b1;
      end
      else begin
         s_axis_tready <= 1'b0;
      end
   end

   // icounter increment block
   always @(posedge clk) begin
      if (icounter_extended < buffer_length) begin
         if (m_axis_tvalid_buff[0]) begin
            icounter <= icounter + 1'b1;
         end
      end
      else if (icounter_extended == buffer_length && m_axis_tready) begin
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

   always @(posedge clk) begin
      if (m_axis_tvalid_buff[0] == 1'b1) begin
         argsum <= i_square + q_square;
      end
   end

   always @(posedge clk) begin
      if (icounter_buff_extended == buffer_length) begin
         out_max <= argsum;
         index <= icounter;
      end
      else if (argsum > out_max) begin
         out_max <= argsum;
         index <= icounter_buff;
      end
      else begin
         out_max <= out_max;
         index <= index;
      end
   end // always @ (posedge clk)

   always @(posedge clk) begin
      if (icounter_extended == buffer_length) begin
         s_axis_tvalid <= 1'b1;
      end else begin
         s_axis_tvalid <= 1'b0;
      end
   end

   initial begin
      $dumpfile("arg_max.vcd");
      $dumpvars(2, arg_max);
   end

endmodule // argmax
