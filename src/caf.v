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
    input                                  s_axis_freq_step_tready,
    input [phase_bits - 1:0]               freq_step,
    input                                  s_axis_freq_step_valid,
    output reg                             m_axis_freq_step_tready,
    output [foas_counter_bits - 1:0]       freq_step_index,
    output reg                             freq_step_index_tvalid,
    input                                  neg_shift,
    input                                  m_axis_tvalid,
    input [xi_bits - 1:0]                  xi,
    input [xq_bits - 1:0]                  xq,
    input [yi_bits - 1:0]                  yi,
    input [yq_bits - 1:0]                  yq,
    output                                 s_axis_tready,
    input                                  m_axis_tready,
    output reg [out_max_bits -1:0]         out_max,
    output reg [foas_counter_bits - 1:0]   foas_index,
    output reg [length_counter_bits - 1:0] time_index,
    output reg                             s_axis_tvalid);

   parameter                           INCREMENT_INIT = 3'b000;
   parameter                           IDLE = 3'b001;
   parameter                           CORRELATE = 3'b010;
   parameter                           FIND_MAX = 3'b011;
   parameter                           RETURN_MAX = 3'b100;

   reg                                 all_freq_steps_set;
   reg [2:0]                           state;
   wire                                foas_last_index;

   // FOAS
   reg                                 foas_transaction_started;
   reg [foas_counter_bits-1:0]         foas_index_counter;
   reg [foas-1:0]                      foas_index_valid;
   reg [foas-1:0]                      neg_shift_index;
   reg [phase_bits - 1:0]              freq_step_capture_buff;
   wire [31:0]                         foas_index_counter_extended;

   // Slices
   wire [foas-1:0]                     s_axis_tready_slice;
   reg [foas-1:0]                      all_slice_static_cmp;
   wire [foas-1:0]                     m_axis_tready_slice;
   wire [out_max_bits-1:0]             out_max_slice [foas-1:0];
   wire [length_counter_bits-1:0]      index_slice[foas-1:0];
   wire [foas-1:0]                     s_axis_tvalid_slice;

   // Max
   reg [foas-1:0]                      m_axis_tready_find_max;
   reg [out_max_bits - 1:0]            out_max_buff;
   reg [foas_counter_bits -1:0]        foas_index_buff;
   reg [length_counter_bits - 1:0]     time_index_buff;

   assign freq_step_index = foas_index_counter[foas_counter_bits - 1:0];
   assign foas_index_counter_extended = { {(32 - foas_counter_bits){1'b0}}, foas_index_counter};
   assign foas_last_index = foas_index_counter_extended == (foas - 1);

   assign m_axis_tready_slice = (s_axis_tvalid_slice == all_slice_static_cmp) ?
                                m_axis_tready_find_max :
                                ((state == CORRELATE) & m_axis_tready) ?
                                all_slice_static_cmp :
                                m_axis_tready_find_max;

   assign s_axis_tready = (s_axis_tready_slice == all_slice_static_cmp) &&
                          (s_axis_tvalid_slice != all_slice_static_cmp) &&
                          (state == CORRELATE || state == IDLE);

   initial begin
      all_slice_static_cmp = -'d1;
      m_axis_freq_step_tready = 1'b0;
      s_axis_tvalid = 1'b0;
      foas_index_counter = 'd0;
      state = 'd0;
      m_axis_tready_find_max = 'd0;
      out_max = 'd0;
      foas_index = 'd0;
      time_index = 'd0;
   end

   always @(posedge clk) begin
      case (state)
        INCREMENT_INIT: begin
           if (foas_last_index && (s_axis_freq_step_valid == 1'b1)) begin
              state <= CORRELATE;
              all_freq_steps_set <= 1'b1;
           end else begin
              state <= state;
              all_freq_steps_set <= all_freq_steps_set;
           end
        end
        CORRELATE: begin
           if (s_axis_tvalid_slice == all_slice_static_cmp) begin
              state <= FIND_MAX;
           end else begin
              state <= state;
           end
        end
        FIND_MAX: begin
           if (foas_last_index) begin
              state <= RETURN_MAX;
           end
        end
        RETURN_MAX: begin
           if (m_axis_tready) begin
              state <= IDLE;
           end
        end
        IDLE: begin
           if (m_axis_tvalid) begin
              state <= CORRELATE;
           end
           else if (s_axis_freq_step_tready) begin
              state <= INCREMENT_INIT;
           end
        end
        default: begin
           state <= state;
           all_freq_steps_set <= all_freq_steps_set;
        end
      endcase // case (state)
   end // always @ (posedge clk)

   always @(posedge clk) begin
      case (state)
        INCREMENT_INIT: begin
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
           end // else: !if(s_axis_freq_step_valid)
        end // case: INCREMENT_INIT
        FIND_MAX: begin
           m_axis_tready_find_max <= 1'b1 << foas_index_counter;
           // Increment counter
           if (foas_last_index) begin
              foas_index_counter <= 'd0;
           end
           else begin
              foas_index_counter <= foas_index_counter + 1'b1;
           end
           // Find max logic
           if (out_max_slice[foas_index_counter] > out_max_buff) begin
              foas_index_buff <= foas_index_counter;
              time_index_buff <= index_slice[foas_index_counter];
              out_max_buff <= out_max_slice[foas_index_counter];
           end
        end // case: FIND_MAX
        RETURN_MAX: begin
           foas_index <= foas_index_buff;
           time_index <= time_index_buff;
           out_max <= out_max_buff;
           s_axis_tvalid <= (s_axis_tvalid == 1'b0) ? 1'b1 : (m_axis_tready) ? 1'b0 : s_axis_tvalid;
        end
        default: begin
           // INCREMENT INIT
           m_axis_freq_step_tready <= 1'b0;
           foas_index_counter <= 'd0;
           foas_index_valid <= 'd0;
           freq_step_capture_buff <= freq_step_capture_buff;
           // FIND MAX
           out_max <= 'd0;
           foas_index <= 'd0;
           m_axis_tready_find_max <= 'd0;
           out_max_buff <= 'd0;
           // RETURN MAX
           s_axis_tvalid <= 1'b0;
        end // case: default
      endcase // case (state)
   end // always @ (posedge clk)

   // CAF Slices
   genvar i;

   generate
      for (i = 0; i < foas; i = i + 1) begin
         caf_slice #(.phase_bits(phase_bits),
                     .xi_bits(xi_bits),
                     .xq_bits(xq_bits),
                     .yi_bits(yi_bits),
                     .yq_bits(yq_bits),
                     .i_bits(i_bits),
                     .q_bits(q_bits),
                     .length(length),
                     .length_counter_bits(length_counter_bits),
                     .out_max_bits(out_max_bits)
                     ) caf_slice_inst(.clk(clk),
                                      .freq_step(freq_step_capture_buff),
                                      .freq_step_valid(foas_index_valid[i]),
                                      .neg_shift(neg_shift_index[i]),
                                      .m_axis_tvalid(m_axis_tvalid),
                                      .xi(xi),
                                      .xq(xq),
                                      .yi(yi),
                                      .yq(yq),
                                      .s_axis_tready(s_axis_tready_slice[i]),
                                      .m_axis_tready(m_axis_tready_slice[i]),
                                      .out_max(out_max_slice[i]),
                                      .index(index_slice[i]),
                                      .s_axis_tvalid(s_axis_tvalid_slice[i])
                                      );
      end // for (i = 0; i < foas; i = i + 1)
   endgenerate

   initial begin
      $dumpfile("caf.vcd");
      $dumpvars(1, caf);
   end

endmodule // caf
