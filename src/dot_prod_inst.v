dot_prod #(.xi_bits({{ xi_bits }}),
           .xq_bits({{ xq_bits }}),
           .yi_bits({{ yi_bits }}),
           .yq_bits({{ yq_bits }}),
           .i_bits({{ sum_i_size }}),
           .q_bits({{ sum_i_size }}),
           .length({{ length }}),
           .sum_i_size({{ sum_i_size }}),
           .sum_q_size({{ sum_q_size }})
           ) {{ dot_prod_name }} (.clk(clk),
                                  .m_axis_product_tready(m_axis_product_tready),
                                  .m_axis_x_tvalid(m_axis_x_tvalid),
                                  .xi(xi),
                                  .xq(xq),
                                  .m_axis_y_tvalid(m_axis_y_tvalid),
                                  .yi(yi),
                                  .yq(yq),
                                  .s_axis_product_tvalid(s_axis_product_tvalid),
                                  .i(i),
                                  .q(q)
                                  );

