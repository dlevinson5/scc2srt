import re
import logging
import sys
import scc2srt
import os

if __name__ == "__main__":

    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=log_format)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    logHandler = logging.StreamHandler(sys.stdout)
    logHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(log_format)
    logHandler.setFormatter(formatter)

    logger.addHandler(logHandler)

    files = [f for f in os.listdir('Z:\\tmp\\_SRC') if re.match('.*.*\.scc', f)]

    for f in files:
        input_file = '{}{}'.format('Z:\\tmp\\_SRC\\', f)
        output_file = 'Z:\\tmp\\_OUTPUT\\{}.vtt'.format(os.path.splitext(f)[0])
        print(input_file)
        items = scc2srt.parse(input_file, logger, 3600)
        scc2srt.write_srt(items, 0, output_file)
 
    print("done")
    exit(0)


 