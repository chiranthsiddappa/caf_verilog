{{ sig_gen_name }} #(.phase_bits({{ phase_bits }}),
                     .n_bits({{ n_bits }}),
                     .lut_length({{ lut_length }})) {{ sig_gen_inst_name }}(.clk(clk),
                                                                            .m_axis_data_tready(m_axis_data_tready),
                                                                            .m_axis_freq_step_tvalid(m_axis_freq_step_tvalid),
                                                                            .freq_step(freq_step),
                                                                            .cosine(cosine),
                                                                            .sine(sine),
                                                                            .s_axis_data_tvalid(s_axis_data_tvalid));
