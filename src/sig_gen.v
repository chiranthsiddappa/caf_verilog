`timescale 1ns/1ns

module {{ sig_gen_name }} #(parameter phase_bits = 32,
                 parameter n_bits = 7,
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
   reg [1:0]                freq_step_set;
   wire                     phase_increment_m_axis_condition;
   wire                     phase_increment_step_condition;
   wire                     s_axis_valid_condition;

   assign phase_increment_m_axis_condition = (m_axis_data_tready & (freq_step_set[1] | freq_step_set[0]));
   assign phase_increment_step_condition = freq_step_set[0] & ~freq_step_set[1];
   assign s_axis_valid_condition = (freq_step_set[0] & ~freq_step_set[1]) | (m_axis_data_tready & freq_step_set[1]);

   initial begin
      s_axis_data_tvalid = 1'b0;
      phase = {phase_bits{1'b0}};
      phase_4 = {phase_bits{1'b1}} / 'd4;
      freq_step_buff = 'd0;
      freq_step_set = 2'b0;
      $readmemb("{{ lut_filename }}", lut);
   end

   always @(posedge clk) begin
      if (m_axis_freq_step_tvalid) begin
            freq_step_buff <= freq_step;
            freq_step_set[0] <= 1'b1;
      end else begin
         freq_step_set[0] <= freq_step_set[0];
      end
   end

   always @(posedge clk) begin
      if (freq_step_set[1] & m_axis_freq_step_tvalid) begin
         if (freq_step_buff != freq_step) begin
            freq_step_set[1] <= 1'b0;
         end else begin
            freq_step_set[1] <= freq_step_set[0];
         end
      end
      else begin
         freq_step_set[1] <= freq_step_set[0];
      end
   end

   always @(posedge clk) begin
      if (phase_increment_step_condition | phase_increment_m_axis_condition) begin
         phase <= phase + freq_step_buff;
         phase_4 <= phase_4 + freq_step_buff;
      end
      else begin
         phase <= phase;
         phase_4 <= phase_4;
      end
   end // always @ (posedge clk)

   always @(posedge clk) begin
      if (s_axis_valid_condition) begin
         sine <= lut[phase[phase_bits - 1:phase_bits - n_bits - 1]];
         cosine <= lut[phase_4[phase_bits - 1:phase_bits - n_bits - 1]];
         s_axis_data_tvalid <= 1'b1;
      end
      else begin
         sine <= sine;
         cosine <= cosine;
         s_axis_data_tvalid <= freq_step_set[1];
      end
   end // always @ (posedge clk)

   initial begin
      $dumpfile("{{ sig_gen_name }}.vcd");
      $dumpvars(2, {{ sig_gen_name }});
   end

endmodule // sig_gen
