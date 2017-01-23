import scc2srt.backend


def scc2srt(input_file: str, output_file: str):

    items = backend.parse(input_file)

    backend.write_srt(items, output_file)
