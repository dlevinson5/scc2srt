import scc2srt.scc2srt


def convert(input_file: str, output_file: str, logger: None):
 
    items = scc2srt.parse(input_file, logger)

    scc2srt.write_srt(items, output_file)
