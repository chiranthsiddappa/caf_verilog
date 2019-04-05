`timescale 1ns/1ns

module reference_buffer #(parameter buffer_length = 10,
                          parameter index_bits = 4,
                          parameter i_bits = 12,
                          parameter q_bits = 12
                          )
   (input clk,
    input                            m_axi_rready,
    input                            m_axi_rvalid,
    input [index_bits - 1:0]         m_axi_raddr,
    output reg                       s_axi_rready,
    output reg signed [i_bits - 1:0] i,
    output reg signed [q_bits - 1:0] q,
    output reg                       s_axi_rvalid
    );

   reg                               m_valid;
   reg [i_bits + q_bits - 1:0]       buffer [0:buffer_length - 1];
   reg [index_bits - 1:0]            addr_buffer;

   initial begin
      $readmemb("{{ reference_buffer_filename }}", buffer);
      s_axi_rvalid = 1'b0;
      s_axi_rready = 1'b0;
      m_valid = 1'b0;
   end

   always @(posedge clk) begin
      m_valid <= m_axi_rvalid;
      if (m_axi_rvalid) begin
         addr_buffer <= m_axi_raddr;
      end
   end

   always @(posedge clk) begin
      s_axi_rready <= m_axi_rready | ~s_axi_rvalid;
      if (m_valid && (addr_buffer < buffer_length)) begin
         i <= buffer[addr_buffer][i_bits + q_bits - 1:q_bits];
         q <= buffer[addr_buffer][q_bits:0];
         s_axi_rvalid <= 1'b1;
      end else if (m_axi_rready) begin
         s_axi_rvalid <= 1'b0;
      end
   end
endmodule // reference_buffer
