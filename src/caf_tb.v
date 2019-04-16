`timescale 1ns/1ns
`define NULL 0

module caf_tb();
   reg clk;
   wire s_axis_tready;
   reg [31:0] m_axis_tdata;
   reg        m_axis_tvalid;
   wire       s_axis_tvalid;
   wire [31:0] s_axis_tdata;
   reg         m_axis_tready;
   integer     caf_input;
   integer     task_output;

   {% include "caf_inst.v" %}

   initial begin
      clk = 1'b0;
      caf_input = $fopen("{{ caf_input }}", "r");
      m_axis_tvalid = 1'b0;
      m_axis_tready = 1'b0;
      if (caf_input == `NULL) begin
         $display("caf_input was NULL");
         $finish;
      end
      @(posedge clk) begin
         task_output = $fscanf(caf_input, "%b\n", m_axis_tdata);
         m_axis_tvalid = 1'b1;
      end
      @(negedge s_axis_tready) m_axis_tready = 1'b1;
      @(posedge s_axis_tvalid);
      @(negedge s_axis_tvalid) m_axis_tready = 1'b0;
      @(posedge clk);
      @(posedge clk) $finish;
   end

   always begin
      #10 clk = ~clk;
   end

   always @(posedge clk) begin
      if (!$feof(caf_input) && s_axis_tready) begin
         $fscanf(caf_input, "%b\n", m_axis_tdata);
         m_axis_tvalid = 1'b1;
      end
      else if ($feof(caf_input)) begin
         m_axis_tvalid = 1'b0;
      end
   end
endmodule // caf_tb
