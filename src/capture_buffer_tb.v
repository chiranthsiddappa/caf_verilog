`timescale 1ns/1ns
`define NULL 0

module capture_buffer_tb();
   reg clk;
   integer write_file;
   reg     m_axi_rready;
   reg     m_axi_rvalid;
   reg [{{ index_bits }} - 1:0] m_axi_raddr;
   wire                         s_axi_rready;
   wire signed [{{ i_bits - 1}}:0] i;
   wire signed [{{ q_bits - 1}}:0] q;
   wire                            s_axi_rvalid;
   reg [{{ index_bits - 1}}:0]     m_axi_waddr;
   reg                             m_axi_wvalid;
   wire                            s_axi_wready;
   reg [{{ i_bits + q_bits - 1}}:0] m_axi_wdata;
   wire                             s_axi_bresp;
   wire                             s_axi_bvalid;
   reg                              m_axi_bready;
   reg [{{ i_bits + q_bits - 1 }}:0] buffer_values [0: {{ buffer_length - 1 }}];

   initial begin
      clk = 1'b0;
      m_axi_rready = 1'b0;
      m_axi_rvalid = 1'b0;
      m_axi_raddr = 'd0;
      write_file = $fopen("{{ test_output_filename }}");
      if (write_file == `NULL) begin
         $display("capture_buffer_output_filename handle was NULL");
         $finish;
      end
      $readmemb("{{ capture_buffer_filename }}", buffer_values);
      m_axi_waddr = 'd0;
      m_axi_wvalid = 1'b1;
      m_axi_wdata = buffer_values['d0];
      @(posedge clk) begin
         m_axi_rvalid = 1'b1;
         m_axi_rready = 1'b1;
      end // UNMATCHED !!
      @(posedge clk) m_axi_raddr = 'd1;
   end // initial begin

   {% include "capture_buffer_inst.v" %}

     always begin
        #10 clk = ~clk;
     end

   always @(posedge clk) begin
      if (s_axi_wready) begin
         if (m_axi_waddr < {{ buffer_length }}) begin
            m_axi_waddr = m_axi_waddr + 1'b1;
            m_axi_wdata = buffer_values[m_axi_waddr];
            m_axi_wvalid = 1'b1;
         end else begin
            m_axi_wvalid = 1'b0;
         end
      end
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
