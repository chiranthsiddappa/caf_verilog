reference_buffer #(.buffer_length({{ buffer_length }}),
                   .buffer_bits({{ buffer_bits }}),
                   .i_bits({{ i_bits }}),
                   .q_bits({{ q_bits }})
                   {{ reference_buffer_name }} (.clk(clk),
                                                .m_axis_tready(m_axis_tready),
                                                .m_axis_index_tvalid(m_axis_index_tvalid),
                                                .m_axis_index_tdata(m_axis_index_tdata),
                                                .s_axis_data_tready(s_axis_data_tready),
                                                .i(i),
                                                .q(q),
                                                .s_axis_data_tvalid(s_axis_data_tvalid)
                                                );
