reference_buffer #(.buffer_length({{ ref_buffer_length }}),
                   .index_bits({{ ref_index_bits }}),
                   .i_bits({{ ref_i_bits }}),
                   .q_bits({{ ref_q_bits }}))
                   {{ reference_buffer_name }} (.clk(clk),
                                                .m_axi_rready(m_axi_ref_rready),
                                                .m_axi_rvalid(m_axi_ref_rvalid),
                                                .m_axi_raddr(m_axi_ref_raddr),
                                                .s_axi_rready(s_axi_ref_rready),
                                                .i(ref_i),
                                                .q(ref_q),
                                                .s_axi_rvalid(s_axi_ref_rvalid)
                                                );
