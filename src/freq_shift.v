`timescale 1ns/1ns

module {{ freq_shift_name }} #(parameter phase_bits = 32,
                               parameter i_bits = 12,
                               parameter q_bits = 12
                               )
   (                        input clk,
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
   wire signed [{{ n_bits - 1 }}:0]                      cosine;
   reg signed [{{ n_bits - 1 }}:0]                       cosine_buff;
   wire signed [{{ n_bits - 1 }}:0]                      sine;
   reg signed [{{ n_bits - 1 }}:0]                       sine_buff;
   wire                                                  s_axis_sig_gen_tvalid;
   reg                                                   s_axis_sig_gen_tvalid_buff;
   wire                                                  m_axis_mult_tvalid;
   reg signed [i_bits - 1:0]                             xi_buff [0:2];
   reg signed [q_bits - 1:0]                             xq_buff [0:2];
   reg [2:0]                                             m_axis_tvalid_buff;

   initial begin
      m_axis_tvalid_buff = 3'b0;
   end

   always @(posedge clk) begin
      if (m_axis_tvalid) begin
         m_axis_tvalid_buff <= (m_axis_tvalid_buff << 1) | m_axis_tvalid;
      end else begin
         m_axis_tvalid_buff <= m_axis_tvalid_buff >> 1;
      end
   end

   always @(posedge clk) begin
      if (m_axis_tvalid | m_axis_tvalid_buff) begin
         xi_buff[0] <= xi;
         xq_buff[0] <= xq;
         xi_buff[1] <= xi_buff[0];
         xq_buff[1] <= xq_buff[0];
         xi_buff[2] <= xi_buff[1];
         xq_buff[2] <= xq_buff[1];
      end
   end

   always @(posedge clk) begin
      s_axis_sig_gen_tvalid_buff <= s_axis_sig_gen_tvalid;
      if (m_axis_tvalid_buff) begin
         cosine_buff <= cosine;
         if (neg_shift) begin
            sine_buff <= sine * -'d1;
         end else begin
            sine_buff <= sine;
         end
      end
   end // always @ (posedge clk)

   assign m_axis_mult_tvalid = m_axis_tvalid_buff & s_axis_sig_gen_tvalid_buff;
   assign m_axis_sig_gen_tready = m_axis_tvalid_buff;

   {{ sig_gen_name }} #(.phase_bits({{ phase_bits }}),
                        .n_bits({{ n_bits }}),
                        .lut_length({{ lut_length }})) {{ sig_gen_inst_name }}(.clk(clk),
                                                                               .m_axis_data_tready(m_axis_sig_gen_tready),
                                                                               .m_axis_freq_step_tvalid(m_axis_tvalid),
                                                                               .freq_step(freq_step),
                                                                               .cosine(cosine),
                                                                               .sine(sine),
                                                                               .s_axis_data_tvalid(s_axis_sig_gen_tvalid));

   cpx_multiply #(.xi_bits(i_bits),
                  .xq_bits(q_bits),
                  .yi_bits({{ n_bits }}),
                  .yq_bits({{ n_bits }}),
                  .i_bits(i_bits),
                  .q_bits(q_bits)) freq_mult(.clk(clk),
                                             .m_axis_tready(m_axis_tready),
                                             .m_axis_tvalid(m_axis_mult_tvalid),
                                             .xi(xi_buff[2]),
                                             .xq(xq_buff[2]),
                                             .yi(cosine_buff),
                                             .yq(sine_buff),
                                             .s_axis_tready(s_axis_tready),
                                             .i(i),
                                             .q(q),
                                             .s_axis_tvalid(s_axis_tvalid));

endmodule //
