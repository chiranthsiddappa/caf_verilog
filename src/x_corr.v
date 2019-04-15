`timescale 1ns/1ns

module x_corr #(parameter xi_bits = 12,
                parameter xq_bits = 12,
                parameter yi_bits = 12,
                parameter yq_bits = 12,
                parameter i_bits = 24,
                parameter q_bits = 24,
                parameter length = 5,
                parameter length_counter_bits = 3,
                parameter out_max_bits = 5
                )
   (input clk,
    output                             s_axis_tready,
    input [xi_bits - 1:0]              xi,
    input [xq_bits - 1:0]              xq,
    input [yi_bits - 1:0]              yi,
    input [yq_bits - 1:0]              yq,
    input                              m_axis_tvalid,
    input                              m_axis_tready,
    output [out_max_bits - 1:0]        out_max,
    output [length_counter_bits - 1:0] index,
    output                             s_axis_tvalid
    );

   wire                                    s_axis_product_tvalid;
   wire                                    m_axis_x_tvalid;
   wire                                    m_axis_y_tvalid;
   wire                                    m_axis_product_tready;
   wire signed [i_bits - 1:0]              i;
   wire signed [q_bits - 1:0]              q;

   assign m_axis_x_tvalid = m_axis_tvalid;
   assign m_axis_y_tvalid = m_axis_tvalid;
   assign m_axis_product_tready = s_axis_tready;

   {% include "dot_prod_pip_inst.v" %}

                            argmax #(.buffer_length(length + 1),
                                     .index_bits(length_counter_bits + 1),
                                     .out_max_bits(out_max_bits),
                                     .i_bits(i_bits),
                                     .q_bits(q_bits)) arg_max_xc(.clk(clk),
                                                                 .m_axis_tvalid(s_axis_product_tvalid),
                                                                 .xi(i),
                                                                 .xq(q),
                                                                 .s_axis_tready(s_axis_tready),
                                                                 .m_axis_tready(m_axis_tready),
                                                                 .out_max(out_max),
                                                                 .index(index),
                                                                 .s_axis_tvalid(s_axis_tvalid)
                                                                 );
   

endmodule // xcorr
