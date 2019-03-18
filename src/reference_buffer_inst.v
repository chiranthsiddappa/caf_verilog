reference_buffer #(.buffer_length({{ buffer_length }}),
                   .index_bits({{ index_bits }}),
                   .i_bits({{ i_bits }}),
                   .q_bits({{ q_bits }}))
                   {{ reference_buffer_name }} (.clk(clk),
                                                .m_axi_rready(m_axi_rready),
                                                .m_axi_rvalid(m_axi_rvalid),
                                                .m_axi_index_rdata(m_axi_index_rdata),
                                                .s_axi_data_rready(s_axi_data_rready),
                                                .i(i),
                                                .q(q),
                                                .s_axi_data_rvalid(s_axi_data_rvalid)
                                                );
