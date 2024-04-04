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
    output reg [index_bits-1:0]     index,
    output reg                      s_axis_tvalid
    );

   reg signed [index_bits:0]        icounter;
   wire signed [31:0]               icounter_extended;
   reg [i_bits + i_bits - 2:0]      i_square;
   reg [q_bits + q_bits - 2:0]      q_square;
   reg [out_max_bits - 1:0]         argsum;
   reg                              sq_stage_valid;
   reg                              sum_stage_valid;
   wire                             result_collected;
   reg                              result_collected_buff;
   wire                             result_collected_cond;

   initial begin
      index = 'd0;
      s_axis_tready = 1'b0;
      icounter = 'd0;
      out_max = 'd0;
      s_axis_tvalid = 1'b0;
      argsum = 'd0;
   end

   assign icounter_extended = { {(31 - index_bits){icounter[index_bits]}}, icounter};
   assign result_collected = s_axis_tvalid & m_axis_tready;
   assign result_collected_cond = result_collected | result_collected_buff;

   // s_axis_tready block with catch
   always @(posedge clk) begin
      if (icounter_extended < buffer_length) begin
         s_axis_tready <= 1'b1;
      end
      else if ((icounter_extended == buffer_length) | result_collected_cond) begin
         s_axis_tready <= 1'b1;
      end
      else begin
         s_axis_tready <= 1'b0;
      end
   end

   always @(posedge clk) begin
      if (m_axis_tvalid & (s_axis_tready)) begin
         i_square <= xi * xi;
         q_square <= xq * xq;
         sq_stage_valid <= 1'b1;
      end else begin
         i_square <= i_square;
         q_square <= q_square;
         sq_stage_valid <= 1'b0;
      end
   end

   always @(posedge clk) begin
      if (sq_stage_valid) begin
         argsum <= i_square + q_square;
         sum_stage_valid <= 1'b1;
      end
      else if ((icounter_extended == buffer_length -1) && !sq_stage_valid) begin
         argsum <= 'd0;
         sum_stage_valid <= 1'b0;
      end
      else begin
         argsum <= argsum;
         sum_stage_valid <= 1'b0;
      end
   end

   always @(posedge clk) begin
      if ((icounter_extended == 'd0) && !sum_stage_valid && result_collected_cond) begin
         index <= 'd0;
         out_max <= argsum;
      end
      else if ((argsum > out_max) && sum_stage_valid) begin
         index <= icounter[index_bits - 1:0];
         out_max <= argsum;
      end
      else if (sum_stage_valid) begin
         index <= index;
         out_max <= out_max;
      end
      else begin
         index <= index;
         out_max <= out_max;
      end
   end // always @ (posedge clk)

   // icounter increment block
   always @(posedge clk) begin
      if (icounter_extended < (buffer_length - 1)) begin
         if (sum_stage_valid) begin
            icounter <= icounter + 1'b1;
         end else begin
            icounter <= icounter;
         end
      end
      else if (icounter_extended == (buffer_length - 1)) begin
         icounter <= 'd0;
      end else begin
         icounter <= icounter;
      end
   end // always @ (posedge clk)

   always @(posedge clk) begin
      result_collected_buff <= result_collected;
      if (result_collected_cond) begin
         s_axis_tvalid <= 1'b0;
      end
      else if (icounter_extended == (buffer_length - 1)) begin
         s_axis_tvalid <= 1'b1;
      end
      else begin
         s_axis_tvalid <= s_axis_tvalid;
      end
   end

   initial begin
      $dumpfile("arg_max.vcd");
      $dumpvars(1, arg_max);
   end

endmodule // argmax
