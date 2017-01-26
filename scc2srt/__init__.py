import scc2srt.scc2srt
  
def convert(input_file: str, output_file: str, alignment_padding = 0, logger: logging.Logger = None):

    items = scc2srt.parse(input_file, logger)

    scc2srt.write_srt(items, alignment_padding, output_file)

