`timescale 1ns/1ns

module {{ sig_gen_name }} #(parameter phase_bits = 32,
                 parameter n_bits = 8,
                 parameter lut_length = 255
                 )
   (input clk,
    input [phase_bits - 1: 0]        freq_step,
    input                            m_axis_data_tready,
    output reg signed [n_bits - 1:0] cosine,
    output reg signed [n_bits - 1:0] sine,
    output reg                       s_axis_data_tvalid);

   reg [phase_bits - 1:0] phase;
   reg [phase_bits - 1:0] phase_4;
   reg signed [n_bits -1:0] lut [0:lut_length];
   integer                  lut_iter;
   integer                  lut_filehandler;
   integer                  scan_file;

   initial begin
      phase = {phase_bits{1'b0}};
      phase_4 = {phase_bits{1'b1}} / 3'd4;
      lut_filehandler = $fopen("{{ lut_filename }}", "r");
      for (lut_iter = 0; lut_iter <= lut_length; lut_iter = lut_iter + 1) begin
         scan_file = $fscanf(lut_filehandler, "%d\n", lut[lut_iter]);
      end
   end

   always @(posedge clk) begin
      if (m_axis_data_tready) begin
         phase <= phase + freq_step;
         phase_4 <= phase_4 + freq_step;
      end
      else begin
         phase <= phase;
      end
   end

   always @(posedge clk) begin
      if (m_axis_data_tready) begin
         sine <= lut[phase[phase_bits - 1:phase_bits - n_bits - 1]];
         cosine <= lut[phase_4[phase_bits - 1:phase_bits - n_bits - 1]];
         s_axis_data_tvalid <= 1'b1;
      end else begin
         s_axis_data_tvalid <= 1'b0;
      end
   end

endmodule // sig_gen