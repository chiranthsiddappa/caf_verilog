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

   reg    m_r_axi_valid;
   reg [index_bits - 1:0] r_addr_buffer;

   initial begin
      s_axi_rready = 1'b0;
      s_axi_wready = 1'b0;
      s_axi_bvalid = 1'b0;
   end

   always @(posedge clk) begin
      m_r_axi_valid <= m_axi_rvalid & m_axi_rready;
      r_addr_buffer <= m_axi_raddr;
   end

   always @(posedge clk) begin
      if (m_r_axi_valid && (r_addr < buffer_length)) begin
         i <= buffer[r_addr_buffer][i_bits + q_bits - 1:q_bits];
         q <= buffer[r_addr_buffer][q_bits:0];
         s_axi_rvalid <= 1'b1;
      end
      else begin
         s_axi_rvalid <= 1'b0;
      end
   end

   always @(posedge clk) begin
      s_axi_wready <= 1'b1;
      if (m_axi_wvalid && (m_axi_waddr < buffer_length)) begin
         buffer[m_axi_waddr] <= m_axi_wdata;
         s_axi_bvalid <= 1'b1;
      end else begin
         s_axi_bvalid <= 1'b0;
      end
   end
endmodule // capture_buffer
