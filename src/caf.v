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

   reg [{{ ref_index_bits }}:0] ref_iter;
   wire                         m_axi_ref_rready;
   reg                          m_axi_ref_rvalid;
   reg [{{ ref_index_bits - 1}}:0] m_axi_ref_raddr;
   wire                            s_axi_ref_rready;
   wire [{{ ref_i_bits - 1 }}:0]   ref_i;
   wire [{{ ref_q_bits - 1 }}:0]   ref_q;
   wire                            s_axi_ref_rvalid;

   initial begin
      m_axi_ref_rvalid = 1'b0;
      m_axi_ref_raddr = 'd0;
      m_axi_ref_raddr = 'd0;
   end

   {% include "reference_buffer_inst.v" %}

     wire m_axi_cap_rready;
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
      m_axi_cap_raddr = 'd0;
      m_axi_cap_rvalid = 1'b0;
      m_axi_cap_waddr = 'd0;
      m_axi_cap_wdata = 'd0;
      m_axi_cap_wvalid = 1'b0;
   end

`include "caf_state_params.v"

   reg [4:0]                               state;

   initial begin
      state = INIT;
   end

   {% include "capture_buffer_inst.v" %}

     genvar ithFreq;

   reg [{{ ref_index_bits }}:0] cap_start;
   reg [{{ ref_index_bits - 1 }}:0] cap_iter;
   wire [{{ caf_foa_len - 1 }}:0]   m_axis_freq_tvalid;
   reg [{{ freq_shift_phase_bits - 1 }}:0] freq_step_lut [0:{{ caf_foa_len - 1 }}];
   reg                                     neg_shift_lut [0:{{ caf_foa_len - 1 }}];
   reg [{{ freq_shift_phase_bits - 1 }}:0] freq_step [0:{{ caf_foa_len - 1 }}];
   reg                                     neg_shift [0:{{ caf_foa_len - 1 }}];
   wire [{{ cap_i_bits - 1 }}:0]           freq_shift_xi [{{ caf_foa_len - 1 }}:0];
   wire [{{ cap_q_bits - 1 }}:0]           freq_shift_xq [{{ caf_foa_len - 1 }}:0];
   wire [{{ caf_foa_len - 1 }}:0]          s_axis_freq_tready;
   wire [{{ caf_foa_len - 1 }}:0]          m_axis_freq_tready;
   wire [{{ cap_i_bits - 1 }}:0]           i_freq [{{ caf_foa_len - 1 }}:0];
   wire [{{ cap_q_bits - 1 }}:0]           q_freq [{{ caf_foa_len - 1 }}:0];
   wire [{{ caf_foa_len - 1 }}:0]          s_axis_freq_tvalid;
   reg [{{ caf_foa_len_bits }}:0]          freq_assign;

   assign m_axi_cap_rready = &s_axis_freq_tready;

   initial begin
      cap_start = 'd0;
      cap_iter = 'd0;
      $readmemb("{{ caf_phase_increment_filename }}", freq_step_lut);
      $readmemb("{{ caf_neg_shift_filename }}", neg_shift_lut);
      freq_assign = 'd0;
   end

   wire [{{ caf_foa_len - 1 }}:0] s_axis_x_corr_tvalid;
   wire [{{ caf_foa_len - 1 }}:0] s_axis_x_corr_tready;
   wire [{{ out_max_bits - 1 }}:0] out_max [{{ caf_foa_len - 1 }}:0];
   reg [{{ out_max_bits - 1 }}:0]  out_max_buff [{{ caf_foa_len - 1 }}:0];
   reg [{{ cap_i_bits - 1 }}:0]    x_corr_yi [{{ caf_foa_len - 1 }}:0];
   reg [{{ cap_q_bits - 1 }}:0]    x_corr_yq [{{ caf_foa_len - 1 }}:0];
   wire [{{ length_counter_bits }}:0] x_corr_index [{{ caf_foa_len - 1 }}:0];
   reg [{{ length_counter_bits }}:0]  x_corr_index_buff [{{ caf_foa_len - 1 }}:0];
   reg                                m_axis_x_corr_tready;
   reg [{{ caf_foa_len - 1 }}:0]      m_axis_x_corr_tvalid;
   reg [{{ caf_foa_len_bits - 1 }}:0] freq_final;

   initial begin
      m_axis_x_corr_tready = 1'b0;
   end

   assign m_axi_ref_rready = s_axis_x_corr_tready;
   assign m_axis_freq_tvalid = { {{caf_foa_len}}{s_axi_cap_rvalid} };

   reg [{{ out_max_bits - 1 }}:0] out_max_final;
   reg [{{ length_counter_bits - 1}}:0] index_final;
   
   generate
      for (ithFreq = 0; ithFreq < {{ caf_foa_len }}; ithFreq = ithFreq + 1) begin: caf_freq

         assign freq_shift_xi[ithFreq] = cap_i;
         assign freq_shift_xq[ithFreq] = cap_q;
         assign m_axis_freq_tready[ithFreq] = s_axis_x_corr_tready[ithFreq];

         initial begin
            out_max_buff[ithFreq] = 'd0;
            x_corr_index_buff[ithFreq] = 'd0;
         end

         always @(posedge clk) begin
            m_axis_x_corr_tvalid[ithFreq] <= s_axis_freq_tvalid[ithFreq] & s_axi_ref_rvalid;
            x_corr_yi[ithFreq] <= i_freq[ithFreq];
            x_corr_yq[ithFreq] <= q_freq[ithFreq];
            if (&s_axis_x_corr_tvalid) begin
               out_max_buff[ithFreq] <= out_max[ithFreq];
               x_corr_index_buff[ithFreq] <= x_corr_index[ithFreq];
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

         x_corr #(.xi_bits({{ ref_i_bits }}),
                  .xq_bits({{ ref_q_bits }}),
                  .yi_bits({{ cap_i_bits }}),
                  .yq_bits({{ cap_q_bits }}),
                  .i_bits({{ sum_i_bits }}),
                  .q_bits({{ sum_q_bits }}),
                  .length({{ ref_buffer_length }}),
                  .length_counter_bits({{ ref_index_bits }}),
                  .out_max_bits({{ out_max_bits }})
                  ) x_corr_caf (.clk(clk),
                                .s_axis_tready(s_axis_x_corr_tready[ithFreq]),
                                .xi(ref_i),
                                .xq(ref_q),
                                .yi(x_corr_yi[ithFreq]),
                                .yq(x_corr_yq[ithFreq]),
                                .m_axis_tready(m_axis_x_corr_tready),
                                .m_axis_tvalid(m_axis_x_corr_tvalid[ithFreq]),
                                .out_max(out_max[ithFreq]),
                                .index(x_corr_index[ithFreq]),
                                .s_axis_tvalid(s_axis_x_corr_tvalid[ithFreq])
                                );
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
               s_axis_tready <= s_axi_cap_wready;
               s_axis_tvalid <= 1'b0;
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
               m_axi_ref_raddr <= 'd0;
               m_axi_cap_rvalid <= 1'b1;
               m_axi_ref_rvalid <= 1'b1;
               m_axis_x_corr_tready <= 1'b1;
               ref_iter <= 'd0;
            end // if (m_axi_cap_waddr == {{ cap_buffer_length - 1 }})
            else begin
               m_axi_cap_wvalid <= 1'b0;
            end // else: !if(m_axi_cap_waddr == {{ cap_buffer_length - 1 }})
          CORRELATE:
            begin
               // ref logic
               if (ref_iter <= ref_iter <= {{ ref_buffer_length }}) begin
                  if (m_axi_ref_raddr < {{ ref_buffer_length - 1 }}) begin
                     if (s_axis_freq_tvalid) begin
                        m_axi_ref_raddr <= m_axi_ref_raddr + &s_axis_freq_tvalid;
                     end
                  end else begin
                     ref_iter <= ref_iter + &s_axis_freq_tvalid;
                     m_axi_ref_raddr <= 'd0;
                  end
               end else begin
                  m_axi_ref_rvalid <= 1'b0;
               end
               // cap logic
               if(cap_start <= {{ ref_buffer_length }}) begin
                  if (cap_iter < {{ ref_buffer_length - 1 }}) begin
                     m_axi_cap_rvalid <= 1'b1;
                     m_axi_cap_raddr <= m_axi_cap_raddr + s_axi_cap_rvalid;
                     cap_iter <= cap_iter + s_axi_cap_rvalid;
                  end
                  else begin
                     cap_iter <= 'd0;
                     cap_start <= cap_start + 1'b1;
                     m_axi_cap_raddr <= cap_start + 1'b1;
                  end
               end
               else begin
                  m_axi_cap_rvalid <= 1'b0;
               end // else: !if(cap_start <= {{ ref_buffer_length }})
               if (s_axis_x_corr_tvalid) begin
                  state <= FIND_MAX;
                  m_axis_x_corr_tready <= 1'b0;
                  out_max_final <= 'd0;
                  index_final <= 'd0;
                  freq_assign <= 'd0;
                  freq_final <= 'd0;
               end
            end // case: CORRELATE
          FIND_MAX:
            begin
               $display("freq_assign: %d, s_axis_tvalid: %b, m_axis_tready: %b", freq_assign, s_axis_tvalid, m_axis_tready);
               
               if (freq_assign < {{ caf_foa_len }}) begin
                  freq_assign <= freq_assign + 1'b1;
                  if (out_max_buff[freq_assign] > out_max_final) begin
                     out_max_final <= out_max_buff[freq_assign];
                     index_final <= x_corr_index[freq_assign];
                     freq_final <= freq_assign;
                  end
               end else begin
                  s_axis_tvalid <= 1'b1;
                  s_axis_tdata <= {index_final, freq_final};
               end // else: !if(freq_assign < {{ caf_foa_len }})
               if (m_axis_tready && freq_assign >= {{ caf_foa_len }}) begin
                  state <= IDLE;
               end
            end
        endcase // case (state)
     end // always @ (posedge clk)

endmodule // caf
