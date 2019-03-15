`timescale 1ns/1ns

module reference_buffer #(parameter buffer_length = 10,
                          parameter buffer_bits = 4,
                          parameter i_bits = 12,
                          parameter q_bits = 12
                          )
   (input clk,
    input                      m_axis_tready,
    input                      m_axis_index_tvalid,
    input [buffer_bits - 1:0]  m_axis_index_tdata,
    output reg                 s_axis_data_tready = 1,
    output reg [xi_bits - 1:0] i,
    output reg [xq_bits - 1:0] q,
    output reg                 s_axis_data_tvalid
    );

  reg [i_bits + q_bits - 1:0] buffer [0:buffer_length];

  initial begin
     $readmemb("{{ reference_buffer_filename }}", buffer);
  end

   always @(posedge clk) begin
      s_axis_data_tvalid <= m_axis_index_tvalid;
      if (m_axis_index_tvalid) begin
         i <= buffer[i_bits - 1:q_bits];
         q <= buffer[q_bits:0];
      end
   end
endmodule // reference_buffer
