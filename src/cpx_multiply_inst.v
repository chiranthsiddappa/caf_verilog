cpx_multiply #(.xi_bits({{ xi_bits }}),
               .xq_bits({{ xq_bits }}),
               .yi_bits({{ yi_bits }}),
               .yq_bits({{ yq_bits }}),
               .i_bits({{ i_bits }}),
               .q_bits({{ q_bits }})) cpx_multiply_tb(.clk(clk),
                                                          .m_axis_tready(m_axis_tready),
                                                          .m_axis_tvalid(m_axis_tvalid),
                                                          .xi(xi),
                                                          .xq(xq),
                                                          .yi(yi),
                                                          .yq(yq),
                                                          .s_axis_tready(s_axis_tready),
                                                          .i(i_out),
                                                          .s_axis_tvalid(s_axis_tvalid),
                                                          .q(q_out));

