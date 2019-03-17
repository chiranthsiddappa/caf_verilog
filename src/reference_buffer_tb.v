`timescale 1ns/1ns
`define NULL 0

module reference_buffer_tb();
   reg clk;
   integer write_file;
   reg     m_axis_tready;
   reg     m_axis_index_tvalid;
   reg [{{ buffer_bits}} - 1:0] m_axis_index_tdata;
   wire                         s_axis_data_tready;
   wire signed [{{ i_bits - 1}}:0] i;
   wire signed [{{ q_bits - 1}}:0] q;
   wire                            s_axis_data_tvalid;

   initial begin
      clk = 1'b0;
      m_axis_tready = 1'b0;
      m_axis_index_tvalid = 1'b0;
      m_axis_index_tdata = 0;
      write_file = $fopen("{{ test_output_filename }}");
      if (write_file == `NULL) begin
         $display("reference_buffer_output_file handle was NULL");
         $finish;
      end
      @(posedge clk) m_axis_index_tvalid = 1'b1;
      @(posedge clk) m_axis_tready = 1'b1;
      @(posedge clk) m_axis_index_tdata = 1;
   end

   {% include "reference_buffer_inst.v" %}

     always begin
        #10 clk = ~clk;
     end

   always @(posedge clk) begin
      if (s_axis_data_tvalid) begin
         $fwrite(write_file, "%d,%d\n", i, q);
      end
      if (m_axis_index_tdata < {{ buffer_length }} && s_axis_data_tvalid) begin
         m_axis_tready = 1'b1;
         m_axis_index_tvalid = 1'b1;
         m_axis_index_tdata = m_axis_index_tdata + 1'b1;
      end
      else if (m_axis_index_tdata == {{ buffer_length }}) begin
         m_axis_index_tvalid <= 1'b0;
         m_axis_tready <= 1'b0;
         $fclose(write_file);
         $finish;
      end
   end
endmodule // reference_buffer_tb
