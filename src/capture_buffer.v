`timescale 1ns/1ns

module capture_buffer #(parameter buffer_length = 10,
                        parameter index_bits = 4,
                        parameter i_bits = 12,
                        parameter q_bits = 12,
                        C_INTERCONNECT_DATA_WIDTH = 32
                        )
   (input clk,
    // AXI Read Transaction Signals
    input                            m_axi_rready,
    input                            m_axi_rvalid,
    input [index_bits - 1:0]         m_axi_raddr,
    output reg                       s_axi_rready,
    output reg signed [i_bits - 1:0] i,
    output reg signed [q_bits - 1:0] q,
    output reg                       s_axis_rvalid,
    // AXI Write Transaction Signals
    input [index_bits - 1:0]         m_axi_waddr,
    input                            m_axi_wvalid,
    output reg                       s_axi_wready,
    input [31:0]                     m_axi_wdata,
    output reg s_axi_bresp,
    output reg s_axi_bvalid,
    input m_axi_bready
    );

endmodule // capture_buffer
