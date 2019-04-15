`timescale 1ns/1ns
`define NULL 0

module capture_buffer_tb();
   reg                               clk;
   integer                           write_file;
   reg                               m_axi_cap_rready;
   reg                               m_axi_cap_rvalid;
   reg [{{ cap_index_bits }} - 1:0]  m_axi_cap_raddr;
   wire                              s_axi_cap_rready;
   wire signed [{{ cap_i_bits - 1}}:0] cap_i;
   wire signed [{{ cap_q_bits - 1}}:0] cap_q;
   wire                                s_axi_cap_rvalid;
   reg [{{ cap_index_bits - 1}}:0]     m_axi_cap_waddr;
   reg                                 m_axi_cap_wvalid;
   wire                                s_axi_cap_wready;
   reg [{{ cap_i_bits + cap_q_bits - 1}}:0] m_axi_cap_wdata;
   wire                                     s_axi_cap_bresp;
   wire                                     s_axi_cap_bvalid;
   reg                                      m_axi_cap_bready;
   reg [{{ cap_i_bits + cap_q_bits - 1 }}:0] buffer_values [0: {{ cap_buffer_length - 1 }}];

   initial begin
      clk = 1'b0;
      m_axi_cap_rready = 1'b0;
      m_axi_cap_rvalid = 1'b0;
      m_axi_cap_raddr = 'd0;
      write_file = $fopen("{{ test_output_filename }}");
      if (write_file == `NULL) begin
         $display("capture_buffer_output_filename handle was NULL");
         $finish;
      end
      $readmemb("{{ capture_buffer_filename }}", buffer_values);
      m_axi_cap_waddr = 'd0;
      m_axi_cap_wvalid = 1'b1;
      m_axi_cap_wdata = buffer_values['d0];
      @(posedge clk);
      @(posedge clk);
      @(posedge clk) begin
         m_axi_cap_rvalid = 1'b1;
         m_axi_cap_rready = 1'b0;
      end // UNMATCHED !!
      @(posedge clk) begin
         m_axi_cap_rready = 1'b1;
      end
      @(posedge clk) begin
         m_axi_cap_rready = 1'b0;
      end
      @(posedge clk) begin
         m_axi_cap_rready = 1'b1;
      end
   end // initial begin

   {% include "capture_buffer_inst.v" %}

     always begin
        #10 clk = ~clk;
     end

   always @(posedge clk) begin
      if (s_axi_cap_wready) begin
         if (m_axi_cap_waddr < {{ cap_buffer_length }}) begin
            m_axi_cap_waddr = m_axi_cap_waddr+ 1'b1;
            m_axi_cap_wdata = buffer_values[m_axi_cap_waddr];
            m_axi_cap_wvalid = 1'b1;
         end else begin
            m_axi_cap_wvalid = 1'b0;
         end
      end
   end

   always @(posedge clk) begin
      if (s_axi_cap_rvalid && m_axi_cap_rready) begin
         m_axi_cap_rvalid = 1'b1;
         m_axi_cap_raddr = m_axi_cap_raddr+ 1'b1;
         $fwrite(write_file, "%d,%d\n", cap_i, cap_q);
      end
      else if (m_axi_cap_raddr == {{ cap_buffer_length }} && !s_axi_cap_rvalid) begin
         m_axi_cap_rvalid <= 1'b0;
         m_axi_cap_rready <= 1'b0;
         $fclose(write_file);
         $finish;
      end
   end // always @ (posedge clk)
endmodule // capture_vuffer_tb
