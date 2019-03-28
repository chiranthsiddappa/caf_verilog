`timescale 1ns/1ns

module {{ freq_shift_name }} #(parameter phase_bits = 32,
                               parameter i_bits = 12,
                               parameter q_bits = 12
                               )
   (                        input clk,
                            input                        m_axis_tvalid,
                            input [phase_bits - 1:0]     freq_step,
                            input signed [i_bits - 1:0]  xi,
                            input signed [q_bits - 1:0]  xq,
                            output                       s_axis_tready,
                            input                        m_axis_tready,
                            output signed [i_bits - 1:0] i,
                            output signed [q_bits - 1:0] q,
                            output                       s_axis_tvalid
                            );

   wire signed [{{ n_bits - 1 }}:0]                      cosine;
   wire signed [{{ n_bits - 1 }}:0]                      sine;
   wire                                                  s_axis_sig_gen_tvalid;
   wire                                                  m_axis_mult_tvalid;
   reg signed [i_bits - 1:0]                             xi_buff;
   reg signed [q_bits - 1:0]                             xq_buff;

   always @(posedge clk) begin
      if (m_axis_tvalid) begin
         xi_buff <= xi;
         xq_buff <= xq;
      end
   end

   assign m_axis_mult_tvalid = m_axis_tvalid & s_axis_sig_gen_tvalid;


   {{ sig_gen_name }} #(.phase_bits({{ phase_bits }}),
                        .n_bits({{ n_bits }}),
                        .lut_length({{ lut_length }})) {{ sig_gen_inst_name }}(.clk(clk),
                                                                               .m_axis_data_tready(s_axis_tready),
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
                                             .xi(xi_buff),
                                             .xq(xq_buff),
                                             .yi(cosine),
                                             .yq(sine),
                                             .s_axis_tready(s_axis_tready),
                                             .i(i),
                                             .q(q),
                                             .s_axis_tvalid(s_axis_tvalid));

endmodule //
