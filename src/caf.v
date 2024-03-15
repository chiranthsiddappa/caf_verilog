`timescale 1ns/1ns

module caf #(parameter phase_bits = 10,
             parameter xi_bits = 12,
             parameter xq_bits = 12,
             parameter yi_bits = 12,
             parameter yq_bits = 12,
             parameter i_bits = 24,
             parameter q_bits = 24,
             parameter length = 5,
             parameter length_counter_bits = 3,
             parameter foas = 3,
             parameter foas_counter_bits = 3,
             parameter out_max_bits = 64
             )
   (input clk,
    input                              s_axis_freq_step_tready,
    input [phase_bits - 1:0]           freq_step,
    input                              s_axis_freq_step_valid,
    output reg                         m_axis_freq_step_tready,
    output [foas_counter_bits - 1:0]   freq_step_index,
    output reg                         freq_step_index_tvalid,
    input                              neg_shift,
    input                              m_axis_tvalid,
    input [xi_bits - 1:0]              xi,
    input [xq_bits - 1:0]              xq,
    input [yi_bits - 1:0]              yi,
    input [yq_bits - 1:0]              yq,
    output                             s_axis_tready,
    input                              m_axis_tready,
    output [out_max_bits -1:0]         out_max,
    output [length_counter_bits - 1:0] index,
    output reg                         s_axis_tvalid);

   parameter                           INCREMENT_INIT = 3'b000;
   parameter                           IDLE = 3'b001;
   parameter                           CORRELATE = 3'b010;
   parameter                           FIND_MAX = 3'b011;
   parameter                           RETURN_MAX = 3'b100;

   reg                                 all_freq_steps_set;
   reg [2:0]                           state;

   // FOAS
   reg                                 foas_transaction_started;
   reg [foas_counter_bits:0]           foas_index_counter;
   reg [foas-1:0]                      foas_index_valid;
   reg [foas-1:0]                      neg_shift_index;
   reg [phase_bits - 1:0]              freq_step_capture_buff;
   wire [31:0]                         foas_index_counter_extended;

   assign freq_step_index = foas_index_counter[foas_counter_bits - 1:0];
   assign foas_index_counter_extended = { {(31 - foas_counter_bits){1'b0}}, foas_index_counter};

   initial begin
      m_axis_freq_step_tready = 1'b0;
      freq_step_index = 'd0;
      s_axis_tvalid = 1'b0;
      foas_index_counter = 'd0;
      state = 'd0;
   end

   always @(posedge clk) begin
      case (state)
        INCREMENT_INIT: begin
           if ((foas_index_counter_extended == (foas - 1)) && (s_axis_freq_step_valid == 1'b1)) begin
              state <= CORRELATE;
              all_freq_steps_set <= 1'b1;
           end else begin
              state <= state;
              all_freq_steps_set <= all_freq_steps_set;
           end
        end
        CORRELATE: begin
           // TODO: Capture all caf slice outputs
        end
        default: begin
           state <= state;
           all_freq_steps_set <= all_freq_steps_set;
        end
      endcase // case (state)
   end // always @ (posedge clk)

   always @(posedge clk) begin
      if (state == INCREMENT_INIT) begin
         // Output master logic
         if ((foas_index_counter_extended == (foas - 1)) && (s_axis_freq_step_valid == 1'b1)) begin
            m_axis_freq_step_tready <= 1'b0;
            foas_index_counter <= 'd0;
         end
         else if (foas_index_counter_extended < (foas - 1)) begin
            m_axis_freq_step_tready <= 1'b1;
            if (s_axis_freq_step_tready) begin
               foas_index_counter <= foas_index_counter + 1'b1;
            end
         end
         // Internal logic
         if (s_axis_freq_step_valid) begin
            freq_step_capture_buff <= freq_step;
            foas_index_valid <= 1'b1 << foas_index_counter;
            if (neg_shift) begin
               neg_shift_index <= 1'b1 << foas_index_counter;
            end
            else begin
               neg_shift_index <= 'd0;
            end
         end else begin
            freq_step_capture_buff <= freq_step_capture_buff;
            foas_index_valid <= foas_index_valid;
         end
      end else begin
         m_axis_freq_step_tready <= 1'b0;
         foas_index_counter <= 'd0;
         foas_index_valid <= 'd0;
         freq_step_capture_buff <= freq_step_capture_buff;
      end // else: !if(state == INCREMENT_INIT)
   end // always @ (posedge clk)

   initial begin
      $dumpfile("caf.vcd");
      $dumpvars(1, caf);
   end

endmodule // caf
