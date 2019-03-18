`timescale 1ns/1ns

module reference_buffer #(parameter buffer_length = 10,
                          parameter index_bits = 4,
                          parameter i_bits = 12,
                          parameter q_bits = 12
                          )
   (input clk,
    input                            m_axi_rready,
    input                            m_axi_rvalid,
    input [index_bits - 1:0]         m_axi_index_rdata,
    output reg                       s_axi_data_rready,
    output reg signed [i_bits - 1:0] i,
    output reg signed [q_bits - 1:0] q,
    output reg                       s_axi_data_rvalid
    );

   reg                               m_valid;
   reg [i_bits + q_bits - 1:0]       buffer [0:buffer_length - 1];
   reg [index_bits - 1:0]            addr_buffer;

   initial begin
      $readmemb("{{ reference_buffer_filename }}", buffer);
      s_axi_data_rvalid = 1'b0;
      s_axi_data_rready = 1'b1;
      m_valid = 1'b0;
   end

   always @(posedge clk) begin
      m_valid <= m_axi_rvalid & m_axi_rready;
      addr_buffer <= m_axi_index_rdata;
   end

   always @(posedge clk) begin
      if (m_valid && (addr_buffer < buffer_length)) begin
         i <= buffer[addr_buffer] >> q_bits;
         q <= buffer[addr_buffer] & ((1'b1 << q_bits) - 1);
         s_axi_data_rvalid <= 1'b1;
      end else begin
         s_axi_data_rvalid <= 1'b0;
      end
   end
endmodule // reference_buffer
