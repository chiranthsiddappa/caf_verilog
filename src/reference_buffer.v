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

   (* ram_style = "block" *) reg [i_bits + q_bits - 1:0]       buffer [0:buffer_length - 1];

   initial begin
      $readmemb("{{ reference_buffer_filename }}", buffer);
      s_axi_rvalid = 1'b0;
      s_axi_rready = 1'b0;
   end

   always @(posedge clk) begin
      s_axi_rready <= m_axi_rready | ~s_axi_rvalid;
      if (m_axi_rvalid && (m_axi_raddr < buffer_length)) begin
         i <= buffer[m_axi_raddr][i_bits + q_bits - 1:q_bits];
         q <= buffer[m_axi_raddr][q_bits:0];
         s_axi_rvalid <= 1'b1;
      end else if (m_axi_rready) begin
         s_axi_rvalid <= 1'b0;
      end
   end
endmodule // reference_buffer
