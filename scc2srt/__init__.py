import scc2srt.backend

def convert(input_file: str, output_file: str, logger: None):

    items = backend.parse(input_file, logger)

    backend.write_srt(items, output_file)
