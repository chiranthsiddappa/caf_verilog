`timescale 1ns/1ns

module caf(input clk,
           output reg s_axis_tready,
           input      m_axis_tdata,
           input      m_axis_tvalid,
           output reg s_axis_tvalid,
           output reg s_axis_tdata,
           input      m_axis_tready);

   initial begin
      s_axis_tready = 1'b0;
      s_axis_tvalid = 1'b0;
      s_axis_tdata  = 'd0;
   end

   reg                  m_axi_ref_rready;
   reg                  m_axi_ref_rvalid;
   reg                  m_axi_ref_raddr;
   wire                 s_axi_ref_rready;
   wire [{{ ref_i_bits - 1 }}:0] ref_i;
   wire [{{ ref_q_bits - 1 }}:0] ref_q;
   wire                          s_axi_ref_rvalid;

   initial begin
      m_axi_ref_rready = 1'b0;
      m_axi_ref_rvalid = 1'b0;
      m_axi_ref_raddr = 'd0;
      m_axi_raddr = 'd0;
   end
   
   {% include "reference_buffer_inst.v" %}

     reg m_axi_cap_rready;
   wire  m_axi_cap_rvalid;
   reg   m_axi_cap_raddr;
   wire  s_axi_cap_rready;
   wire [{{ rec_i_bits - 1 }}:0] cap_i;
   wire [{{ rec_q_bits - 1 }}:0] cap_q;
   wire                          s_axi_cap_rvalid;
   reg                           m_axi_cap_waddr;
   reg                           m_axi_cap_wvalid;
   wire                          s_axi_cap_wready;
   reg                           m_axi_cap_wdata;
   wire                          s_axi_cap_bresp;
   wire                          s_axi_cap_bvalid;
   wire                          m_axi_cap_bready;

   initial begin
      m_axi_cap_rready = 1'b0;
      m_axi_cap_raddr = 'd0;
      m_axi_cap_waddr = 'd0;
      m_axi_cap_wdata = 'd0;
   end      

   {% include "capture_buffer_inst.v" %}

     endmodule // caf

