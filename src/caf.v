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
   wire                                    m_axi_cap_bready;

   initial begin
      m_axi_cap_rready = 1'b0;
      m_axi_cap_raddr = 'd0;
      m_axi_cap_rvalid = 1'b0;
      m_axi_cap_waddr = 'd0;
      m_axi_cap_wdata = 'd0;
      m_axi_cap_wvalid = 1'b0;
   end

`include "caf_state_params.v"
   
   reg [4:0]                               state;

   initial begin
      freq_assign = 'd0;
      state = INIT;
   end

   {% include "capture_buffer_inst.v" %}

     genvar ithFreq;

   reg [{{ ref_index_bits - 1 }}:0]        cap_start;
   reg [{{ ref_index_bits - 1 }}:0]        cap_iter;
   reg [{{ caf_foa_len - 1 }}:0]           m_axis_freq_tvalid;
   reg [{{ freq_shift_phase_bits - 1 }}:0] freq_step_lut [0:{{ caf_foa_len - 1 }}];
   reg                                     neg_shift_lut [0:{{ caf_foa_len - 1 }}];
   reg [{{ freq_shift_phase_bits - 1 }}:0] freq_step [0:{{ caf_foa_len - 1 }}];
   reg                                     neg_shift [0:{{ caf_foa_len - 1 }}];
   reg [{{ cap_i_bits - 1 }}:0]            freq_shift_xi [{{ caf_foa_len - 1 }}:0];
   reg [{{ cap_q_bits - 1 }}:0]            freq_shift_xq [{{ caf_foa_len - 1 }}:0];
   wire [{{ caf_foa_len - 1 }}:0]          s_axis_freq_tready;
   reg [{{ caf_foa_len - 1 }}:0]           m_axis_freq_tready;
   wire [{{ cap_i_bits - 1 }}:0]           i_freq [{{ caf_foa_len - 1 }}:0];
   wire [{{ cap_q_bits - 1 }}:0]           q_freq [{{ caf_foa_len - 1 }}:0];
   wire [{{ caf_foa_len - 1 }}:0]          s_axis_freq_tvalid;
   reg [{{ caf_foa_len_bits - 1 }}:0]      freq_assign;

   initial begin
      cap_start = 'd0;
      cap_iter = 'd0;
      m_axis_freq_tvalid = 'd0;
      $readmemb("{{ caf_phase_increment_filename }}", freq_step_lut);
      $readmemb("{{ caf_neg_shift_filename }}", neg_shift_lut);
   end

   generate
      for (ithFreq = 0; ithFreq < {{ caf_foa_len }}; ithFreq = ithFreq + 1) begin: caf_freq

         initial begin
            m_axis_freq_tvalid[ithFreq] = 1'b0;
            m_axis_freq_tready[ithFreq] = 1'b0;
         end

         always @(posedge clk) begin
            if (state == CORRELATE) begin
               m_axis_freq_tvalid[ithFreq] <= s_axi_cap_rvalid;
               freq_shift_xi[ithFreq] <= cap_i;
               freq_shift_xq[ithFreq] <= cap_q;
               m_axis_freq_tready[ithFreq] <= 1'b1;
            end
            else begin
               m_axis_freq_tvalid[ithFreq] <= 1'b0;
               m_axis_freq_tready[ithFreq] <= 1'b0;
            end
         end

         {{ freq_shift_name }} #(.phase_bits({{ freq_shift_phase_bits }}),
                                 .i_bits({{ freq_shift_i_bits }}),
                                 .q_bits({{ freq_shift_q_bits }})) freq_shift_caf(.clk(clk),
                                                                                  .m_axis_tvalid(m_axis_freq_tvalid[ithFreq]),
                                                                                  .freq_step(freq_step[ithFreq]),
                                                                                  .neg_shift(neg_shift[ithFreq]),
                                                                                  .xi(freq_shift_xi[ithFreq]),
                                                                                  .xq(freq_shift_xq[ithFreq]),
                                                                                  .s_axis_tready(s_axis_freq_tready[ithFreq]),
                                                                                  .m_axis_tready(m_axis_freq_tready[ithFreq]),
                                                                                  .i(i_freq[ithFreq]),
                                                                                  .q(q_freq[ithFreq]),
                                                                                  .s_axis_tvalid(s_axis_freq_tvalid[ithFreq]));
      end // block: caf_freq_gen
      endgenerate

     always @(posedge clk) begin
        case(state)
          INIT:
            if (freq_assign < {{ caf_foa_len }}) begin
               freq_step[freq_assign] <= freq_step_lut[freq_assign];
               neg_shift[freq_assign] <= neg_shift_lut[freq_assign];
               freq_assign <= freq_assign + 1'b1;
            end
            else begin
               freq_assign <= 'd0;
               state <= IDLE;
            end
          IDLE:
            begin
               s_axis_tready <= 1'b1;
               if (m_axis_tvalid) begin
                  state <= CAPTURE;
                  m_axi_cap_wvalid <= 1'b1;
                  m_axi_cap_waddr <= 'd0;
                  m_axi_cap_wdata <= m_axis_tdata[{{ cap_i_bits + cap_q_bits - 1 }}:0];
               end
               else begin
                  state <= state;
               end
            end
          CAPTURE:
            if (m_axis_tvalid && m_axi_cap_waddr < {{ cap_buffer_length - 1 }}) begin
               m_axi_cap_waddr <= m_axi_cap_waddr + 1'b1;
               m_axi_cap_wdata <= m_axis_tdata[{{ cap_i_bits + cap_q_bits - 1 }}:0];
               m_axi_cap_wvalid <= 1'b1;
            end
            else if (m_axi_cap_waddr == {{ cap_buffer_length - 1 }}) begin
               s_axis_tready <= 1'b0;
               m_axi_cap_wvalid <= 1'b0;
               m_axi_cap_waddr <= 'd0;
               state <= CORRELATE;
               cap_start <= 'd0;
               cap_iter <= 'd0;
               m_axi_cap_raddr <= 'd0;
               m_axi_cap_rvalid <= 1'b1;
               m_axi_cap_rready <= 1'b1;
            end // if (m_axi_cap_waddr == {{ cap_buffer_length - 1 }})
            else begin
               m_axi_cap_wvalid <= 1'b0;
            end // else: !if(m_axi_cap_waddr == {{ cap_buffer_length - 1 }})
          CORRELATE:
            if(cap_start <= {{ ref_buffer_length }}) begin
               if (cap_iter < {{ ref_buffer_length - 1}}) begin
                  m_axi_cap_rvalid <= 1'b1;
                  m_axi_cap_raddr <= m_axi_cap_raddr + (s_axi_cap_rvalid & s_axis_freq_tready);
                  cap_iter <= cap_iter + (s_axi_cap_rvalid & s_axis_freq_tready);
               end
               else begin
                  cap_iter <= 'd0;
                  cap_start <= cap_start + 1'b1;
                  m_axi_cap_raddr <= cap_start + 1'b1;
               end
            end
            else begin
               // Some logic to transition to FIND_MAX
               m_axi_cap_rvalid <= 1'b0;
               m_axi_cap_rready <= 1'b0;
            end
        endcase // case (state)
     end

endmodule // caf
