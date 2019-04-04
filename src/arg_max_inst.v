argmax #(.buffer_length({{ buffer_length }}),
         .index_bits({{ index_bits }}),
         .out_max_bits({{ out_max_bits }}),
         .i_bits({{ i_bits }}),
         .q_bits({{ q_bits }})) arg_max_tb(.clk(clk),
                                           .m_axis_tvalid(m_axis_tvalid),
                                           .xi(xi),
                                           .xq(xq),
                                           .s_axis_tready(s_axis_tready),
                                           .m_axis_tready(m_axis_tready),
                                           .out_max(out_max),
                                           .index(index),
                                           .s_axis_tvalid(s_axis_tvalid)
                                           );
