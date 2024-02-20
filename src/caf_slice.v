`timescale 1ns/1ns

module caf_slice #(parameter phase_bits = 10,
                   parameter xi_bits = 12,
                   parameter xq_bits = 12,
                   parameter yi_bits = 12,
                   parameter yq_bits = 12,
                   parameter i_bits = 24,
                   parameter q_bits = 24,
                   parameter length = 5,
                   parameter length_counter_bits = 3,
                   parameter out_max_bits = 5
                   )
   (input clk,
    input [phase_bits - 1:0]           freq_step,
    input                              freq_step_valid,
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
    output                             s_axis_tvalid
    );


   wire [xi_bits -1:0]                 freq_slice_xi;
   wire [xq_bits -1:0]                 freq_slice_xq;
   wire [yi_bits - 1:0]                freq_slice_yi;
   wire [yq_bits - 1:0]                freq_slice_yq;
   reg [yi_bits -1:0]                  freq_slice_yi_buff [0:4];
   reg [yq_bits -1:0]                  freq_slice_yq_buff [0:4];
   wire                                slice_inputs_valid;
   reg [4:0]                           slice_inputs_valid_buff;

   // freq_shift axi signals
   wire                                s_axis_freq_tvalid;
   wire                                s_axis_freq_tready;
   wire                                m_axis_freq_tready;
   wire                                m_axis_freq_tvalid;

   // x_corr axi signals
   wire                                s_axis_xcorr_tready;
   wire                                s_axis_xcorr_tvalid;
   wire                                m_axis_x_corr_tready;
   wire                                m_axis_x_corr_tvalid;

   assign s_axis_tready = s_axis_freq_tready & s_axis_xcorr_tready;
   assign s_axis_tvalid = s_axis_xcorr_tvalid;
   assign m_axis_x_corr_tready = m_axis_tready;
   assign m_axis_freq_tvalid = m_axis_tvalid;

   assign m_axis_freq_tready = s_axis_xcorr_tready;
   assign m_axis_x_corr_tvalid = s_axis_freq_tvalid & slice_inputs_valid_buff[4];

   assign freq_slice_yi = freq_slice_yi_buff[4];
   assign freq_slice_yq = freq_slice_yq_buff[4];

   initial begin
      slice_inputs_valid_buff = 5'b0_0000;
   end

   always @(posedge clk) begin
      slice_inputs_valid_buff <= (slice_inputs_valid_buff << 1) | { 4'b0000, m_axis_tvalid};
      freq_slice_yi_buff[0] <= yi;
      freq_slice_yq_buff[0] <= yq;
      freq_slice_yi_buff[1:4] <= freq_slice_yi_buff[0:3];
      freq_slice_yq_buff[1:4] <= freq_slice_yq_buff[0:3];
   end

   {{ freq_shift_name }} #(.phase_bits(phase_bits),
                           .i_bits(xi_bits),
                           .q_bits(xq_bits)) freq_shift_caf(.clk(clk),
                                                            .m_axis_tvalid(m_axis_freq_tvalid),
                                                            .freq_step(freq_step),
                                                            .freq_step_valid(freq_step_valid),
                                                            .neg_shift(neg_shift),
                                                            .xi(xi),
                                                            .xq(xq),
                                                            .s_axis_tready(s_axis_freq_tready),
                                                            .m_axis_tready(m_axis_freq_tready),
                                                            .i(freq_slice_xi),
                                                            .q(freq_slice_xq),
                                                            .s_axis_tvalid(s_axis_freq_tvalid));

   x_corr #(.xi_bits(xi_bits),
            .xq_bits(xq_bits),
            .yi_bits(yi_bits),
            .yq_bits(yq_bits),
            .i_bits(i_bits),
            .q_bits(q_bits),
            .length(length),
            .length_counter_bits(length_counter_bits),
            .out_max_bits(out_max_bits)
            ) x_corr_slice (.clk(clk),
                            .s_axis_tready(s_axis_xcorr_tready),
                            .xi(freq_slice_xi),
                            .xq(freq_slice_xq),
                            .yi(freq_slice_yi),
                            .yq(freq_slice_yq),
                            .m_axis_tready(m_axis_x_corr_tready),
                            .m_axis_tvalid(m_axis_x_corr_tvalid),
                            .out_max(out_max),
                            .index(index),
                            .s_axis_tvalid(s_axis_xcorr_tvalid)
                            );

   initial begin
      $dumpfile("caf_slice.vcd");
      $dumpvars(2, caf_slice);
   end

endmodule // caf_slice
