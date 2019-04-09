`timescale 1ns/1ns

module caf(input clk,
           output reg        s_axis_tready,
           input [31:0]      m_axis_tdata,
           input             m_axis_tvalid,
           output reg        s_axis_tvalid,
           output reg [31:0] s_axis_tdata,
           input             m_axis_tready);

   initial begin
      s_axis_tready = 1'b0;
      s_axis_tvalid = 1'b0;
      s_axis_tdata  = 'd0;
   end

   reg                  m_axi_ref_rready;
   reg                  m_axi_ref_rvalid;
   reg [{{ ref_index_bits - 1}}:0] m_axi_ref_raddr;
   wire                            s_axi_ref_rready;
   wire [{{ ref_i_bits - 1 }}:0]   ref_i;
   wire [{{ ref_q_bits - 1 }}:0]   ref_q;
   wire                            s_axi_ref_rvalid;

   initial begin
      m_axi_ref_rready = 1'b0;
      m_axi_ref_rvalid = 1'b0;
      m_axi_ref_raddr = 'd0;
      m_axi_ref_raddr = 'd0;
   end

   {% include "reference_buffer_inst.v" %}

     reg m_axi_cap_rready;
   reg   m_axi_cap_rvalid;
   reg [{{ cap_index_bits - 1}}:0] m_axi_cap_raddr;
   wire                            s_axi_cap_rready;
   wire [{{ cap_i_bits - 1 }}:0]   cap_i;
   wire [{{ cap_q_bits - 1 }}:0]   cap_q;
   wire                            s_axi_cap_rvalid;
   reg [{{ cap_index_bits - 1}}:0] m_axi_cap_waddr;
   reg                             m_axi_cap_wvalid;
   wire                            s_axi_cap_wready;
   reg [{{ cap_i_bits + cap_q_bits - 1 }}:0] m_axi_cap_wdata;
   wire                                      s_axi_cap_bresp;
   wire                                      s_axi_cap_bvalid;
   wire                                      m_axi_cap_bready;

   initial begin
      m_axi_cap_rready = 1'b0;
      m_axi_cap_raddr = 'd0;
      m_axi_cap_rvalid = 1'b0;
      m_axi_cap_waddr = 'd0;
      m_axi_cap_wdata = 'd0;
   end

`include "caf_state_params.v"
   
   reg [3:0] state;

   initial begin
      state = 4'b0;
   end

   {% include "capture_buffer_inst.v" %}

     genvar ithFreq;

   reg [{{ ref_index_bits - 1 }}:0] cap_start;

   initial begin
      cap_start = 'd0;
   end

     always @(posedge clk) begin
        case(state)
          IDLE: 
            if (m_axis_tvalid) begin
               state <= CAPTURE;
               m_axi_cap_wvalid <= 1'b1;
               m_axi_cap_waddr <= 'd0;
               m_axi_cap_wdata <= m_axis_tdata[{{ cap_i_bits + cap_q_bits - 1 }}:0];
            end
            else begin
               state <= state;
            end
          CAPTURE:
            if (m_axis_tvalid) begin
               m_axi_cap_waddr <= m_axi_cap_waddr + 1'b1;
               m_axi_cap_wdata <= m_axis_tdata[{{ cap_i_bits + cap_q_bits - 1 }}:0];
               m_axi_cap_wvalid <= 1'b1;
            end else if (m_axi_cap_waddr == {{ cap_buffer_length - 1 }}) begin
               state <= CORRELATE;
               m_axi_cap_wvalid <= 1'b0;
               m_axi_cap_waddr <= 'd0;
               cap_start <= 'd0;
            end
            else begin
               m_axi_cap_wvalid <= 1'b0;
               m_axi_cap_waddr <= m_axi_cap_waddr;
               m_axi_cap_wdata <= m_axi_cap_wdata;
            end
        endcase // case (state)
     end

endmodule // caf
