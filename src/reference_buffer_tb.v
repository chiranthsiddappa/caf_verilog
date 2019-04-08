`timescale 1ns/1ns
`define NULL 0

module reference_buffer_tb();
   reg                             clk;
   integer                         write_file;
   reg                             m_axi_ref_rready;
   reg                             m_axi_ref_rvalid;
   reg [{{ ref_index_bits}} - 1:0]     m_axi_ref_raddr;
   wire                            s_axi_ref_rready;
   wire signed [{{ ref_i_bits - 1}}:0] ref_i;
   wire signed [{{ ref_q_bits - 1}}:0] ref_q;
   wire                            s_axi_ref_rvalid;

   initial begin
      clk = 1'b0;
      m_axi_ref_rready = 1'b0;
      m_axi_ref_rvalid = 1'b0;
      m_axi_ref_raddr = 0;
      write_file = $fopen("{{ test_output_filename }}");
      if (write_file == `NULL) begin
         $display("reference_buffer_output_file handle was NULL");
         $finish;
      end
      @(posedge clk);      
      @(posedge clk) begin
         m_axi_ref_rvalid = 1'b1;
         m_axi_ref_rready = 1'b1;
      end // UNMATCHED !!
      @(posedge clk) m_axi_ref_raddr = 'd1;
   end

   {% include "reference_buffer_inst.v" %}

     always begin
        #10 clk = ~clk;
     end

   always @(posedge clk) begin
      if (s_axi_ref_rvalid) begin
         $fwrite(write_file, "%d,%d\n", ref_i, ref_q);
      end
      if (m_axi_ref_raddr < {{ ref_buffer_length }} && s_axi_ref_rvalid) begin
         m_axi_ref_rready = 1'b1;
         m_axi_ref_rvalid = 1'b1;
         m_axi_ref_raddr = m_axi_ref_raddr+ 1'b1;
      end
      else if (m_axi_ref_raddr == {{ ref_buffer_length }} && !s_axi_ref_rvalid) begin
         m_axi_ref_rvalid <= 1'b0;
         m_axi_ref_rready <= 1'b0;
         $fclose(write_file);
         $finish;
      end
   end
endmodule // reference_buffer_tb
