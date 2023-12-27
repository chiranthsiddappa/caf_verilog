`timescale 1ns/1ns

module {{ freq_shift_name }} #(parameter phase_bits = 32,
                               parameter i_bits = 12,
                               parameter q_bits = 12
                               ) (
                                  input                        clk,
                                  input                        m_axis_tvalid,
                                  input [phase_bits - 1:0]     freq_step,
                                  input                        neg_shift,
                                  input signed [i_bits - 1:0]  xi,
                                  input signed [q_bits - 1:0]  xq,
                                  output                       s_axis_tready,
                                  input                        m_axis_tready,
                                  output signed [i_bits - 1:0] i,
                                  output signed [q_bits - 1:0] q,
                                  output                       s_axis_tvalid
                            );

   wire                                                  m_axis_sig_gen_tready;
   wire signed [{{ freq_shift_n_bits - 1 }}:0]           cosine;
   reg signed [{{ freq_shift_n_bits - 1 }}:0]            cosine_buff;
   wire signed [{{ freq_shift_n_bits - 1 }}:0]           sine;
   reg signed [{{ freq_shift_n_bits - 1 }}:0]            sine_buff;
   wire                                                  s_axis_sig_gen_tvalid;
   reg                                                   s_axis_sig_gen_tvalid_buff;
   wire                                                  m_axis_mult_tvalid;
   reg                                                   m_axis_tvalid_buff;
   wire                                                  s_axis_mult_tready;
   reg                                                   s_axis_mult_tready_buff;
   reg [i_bits - 1:0]                                    xi_buff;
   reg [q_bits - 1:0]                                    xq_buff;

   // Internal buffers for timing
   always @(posedge clk) begin
      s_axis_sig_gen_tvalid_buff <= s_axis_sig_gen_tvalid;
      s_axis_mult_tready_buff <= s_axis_mult_tready;
      m_axis_tvalid_buff <= m_axis_tvalid;
   end

   // Buffer inputs
   always @(posedge clk) begin
      if (m_axis_tvalid) begin
         xi_buff <= xi;
         if (neg_shift) begin
            xq_buff <= xq_buff * -'d1;
         end else begin
            xq_buff <= xq;
         end
      end
   end // always @ (posedge clk)

   assign m_axis_sig_gen_tready = ~s_axis_sig_gen_tvalid | (m_axis_tvalid & s_axis_mult_tready);
   assign s_axis_tready = s_axis_mult_tready_buff;
   assign m_axis_mult_tvalid = s_axis_sig_gen_tvalid & m_axis_tvalid_buff;

   {{ sig_gen_name }} #(.phase_bits({{ freq_shift_phase_bits }}),
                        .n_bits({{ freq_shift_n_bits }}),
                        .lut_length({{ lut_length }})) {{ sig_gen_inst_name }}(.clk(clk),
                                                                               .m_axis_data_tready(m_axis_sig_gen_tready),
                                                                               .m_axis_freq_step_tvalid(m_axis_tvalid),
                                                                               .freq_step(freq_step),
                                                                               .cosine(cosine),
                                                                               .sine(sine),
                                                                               .s_axis_data_tvalid(s_axis_sig_gen_tvalid));

   cpx_multiply #(.xi_bits(i_bits),
                  .xq_bits(q_bits),
                  .yi_bits({{ freq_shift_n_bits }}),
                  .yq_bits({{ freq_shift_n_bits }}),
                  .i_bits(i_bits),
                  .q_bits(q_bits)) freq_mult(.clk(clk),
                                             .m_axis_tready(m_axis_tready),
                                             .m_axis_tvalid(m_axis_mult_tvalid),
                                             .xi(xi_buff),
                                             .xq(xq_buff),
                                             .yi(cosine),
                                             .yq(sine),
                                             .s_axis_tready(s_axis_mult_tready),
                                             .i(i),
                                             .q(q),
                                             .s_axis_tvalid(s_axis_tvalid));

   initial begin
      $dumpfile("{{ freq_shift_name }}.vcd");
      $dumpvars(2, {{ freq_shift_name }});
   end

endmodule //
