`timescale 1ns/1ns

module {{ sig_gen_name }} #(parameter phase_bits = 32,
                 parameter n_bits = 8,
                 parameter lut_length = 255
                 )
   (input clk,
    input                            m_axis_freq_step_tvalid,
    input [phase_bits - 1: 0]        freq_step,
    input                            m_axis_data_tready,
    output reg signed [n_bits - 1:0] cosine,
    output reg signed [n_bits - 1:0] sine,
    output reg                       s_axis_data_tvalid);

   reg [phase_bits - 1:0] phase;
   reg [phase_bits - 1:0] phase_4;
   reg signed [n_bits -1:0] lut [0:lut_length];
   reg [phase_bits - 1:0]   freq_step_buff;
   reg                      freq_step_set;

   initial begin
      s_axis_data_tvalid = 1'b0;
      phase = {phase_bits{1'b0}};
      phase_4 = {phase_bits{1'b1}} / 3'd4;
      freq_step_buff = 'd0;
      freq_step_set = 1'b0;
      $readmemb("{{ lut_filename }}", lut);
   end

   always @(posedge clk) begin
      if (m_axis_freq_step_tvalid) begin
         freq_step_set <= 1'b1;
         if (freq_step_buff != freq_step) begin
            freq_step_buff <= freq_step;
         end
      end
   end

   always @(posedge clk) begin
      if (m_axis_data_tready & m_axis_freq_step_tvalid) begin
         phase <= phase + freq_step;
         phase_4 <= phase_4 + freq_step;
      end
      else if (m_axis_data_tready & freq_step_set) begin
         phase <= phase + freq_step_buff;
         phase_4 <= phase_4 + freq_step_buff;
      end
      else begin
         phase <= phase;
         phase_4 <= phase_4;
      end
   end

   always @(posedge clk) begin
      if (freq_step_set | m_axis_freq_step_tvalid) begin
         sine <= lut[phase[phase_bits - 1:phase_bits - n_bits - 1]];
         cosine <= lut[phase_4[phase_bits - 1:phase_bits - n_bits - 1]];
         s_axis_data_tvalid <= 1'b1;
      end else begin
         sine <= sine;
         cosine <= cosine;
         s_axis_data_tvalid <= 1'b0;
      end
   end

endmodule // sig_gen
