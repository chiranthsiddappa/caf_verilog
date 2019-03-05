cpx_multiply #(.xi_bits({{ xi_bits }}),
               .xq_bits({{ xq_bits }}),
               .yi_bits({{ yi_bits }}),
               .yq_bits({{ yq_bits }}),
               .i_bits({{ i_out_bits }}),
               .q_bits({{ q_out_bits }})) cpx_multiply_tb(.clk(clk),
                                                          .m_axis_tready(m_axis_tready),
                                                          .m_axis_x_tvalid(m_axis_x_tvalid),
                                                          .xi(xi),
                                                          .xq(xq),
                                                          .m_axis_y_tvalid(m_axis_y_tvalid),
                                                          .yi(yi),
                                                          .yq(yq),
                                                          .s_axis_i_tvalid(s_axis_i_tvalid),
                                                          .i(i_out),
                                                          .s_axis_q_tvalid(s_axis_q_tvalid),
                                                          .q(q_out));

