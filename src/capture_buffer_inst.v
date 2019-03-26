capture_buffer #(.buffer_length({{ buffer_length }}),
                 .index_bits({{ index_bits }}),
                 .i_bits({{ i_bits }}),
                 .q_bits({{ q_bits }}))
                 {{ capture_buffer_name }} (.clk(clk),
                                            .m_axi_rready(m_axi_rready),
                                            .m_axi_rvalid(m_axi_rvalid),
                                            .m_axi_raddr(m_axi_raddr),
                                            .s_axi_rready(s_axi_rready),
                                            .i(i),
                                            .q(q),
                                            .s_axi_rvalid(s_axi_rvalid),
                                            .m_axi_waddr(m_axi_waddr),
                                            .m_axi_wvalid(m_axi_wvalid),
                                            .s_axi_wready(s_axi_wready),
                                            .m_axi_wdata(m_axi_wdata),
                                            .s_axi_bresp(s_axi_bresp),
                                            .s_axi_bvalid(s_axi_bvalid),
                                            .m_axi_bready(m_axi_bready)
                                            );
