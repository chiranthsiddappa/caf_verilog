`timescale 1ns/1ns
`define NULL 0

module capture_buffer_tb();
   reg clk;
   integer write_file;
   integer input_file;
   reg     m_axi_rready;
   reg     m_axi_rvalid;
   reg [{{ index_bits }} - 1:0] m_axi_raddr;
   wire                         s_axi_rready;
   wire signed [{{ i_bits - 1}}:0] i;
   wire signed [{{ q_bits - 1}}:0] q;
   wire                            s_axi_rvalid;
   reg [{{ index_bits }} - 1:0]    m_axi_waddr;
   reg                             m_axi_wvalid;
   wire                            s_axi_wready;
   reg [{{ buffer_bits }} - 1:0]   m_axi_wdata;
   wire                            s_axi_bresp;
   wire                            s_axi_bvalid;
   reg                             m_axi_bready;

   initial begin
      clk = 1'b0;
      m_axi_rready = 1'b0;
      m_axi_rvalid = 1'b0;
      m_axi_raddr = 0;
      write_file = $fopen("{{ test_output_filename }}");
      if (write_file == `NULL) begin
         $display("capture_buffer_output_filename handle was NULL");
         $finish;
      end
      input_file = $fopen("{{ capture_buffer_filename }}");
      if (input_file == `NULL) begin
         $display("capture_buffer_filename handle was NULL");
         $finish;
      end
   end // initial begin

   {% include "capture_buffer_inst.v" %}

     always begin
        #10 clk = ~clk;
     end

   always @(posedge clk) begin
      if (s_axi_rvalid) begin
         $fwrite(write_file, "%d,%d\n", i, q);
      end
      if (m_axi_raddr < {{ buffer_length }} && s_axi_rvalid) begin
         m_axi_rready = 1'b1;
         m_axi_rvalid = 1'b1;
         m_axi_raddr = m_axi_raddr + 1'b1;
      end
      else if (m_axi_raddr == {{ buffer_length }} && !s_axi_rvalid) begin
         m_axi_rvalid <= 1'b0;
         m_axi_rready <= 1'b0;
         $fclose(write_file);
         $finish;
      end
   end // always @ (posedge clk)
endmodule // capture_vuffer_tb
