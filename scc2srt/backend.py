import re
import logging
import sys

_ccTxMatrix = dict()

_ccRowTable = {
    0x11, 0x40, 0x5F,
    0x11, 0x60, 0x7F,
    0x12, 0x40, 0x5F,
    0x12, 0x60, 0x7F,
    0x15, 0x40, 0x5F,
    0x15, 0x60, 0x7F,
    0x16, 0x40, 0x5F,
    0x16, 0x60, 0x7F,
    0x17, 0x40, 0x5F,
    0x17, 0x60, 0x7F,
    0x10, 0x40, 0x5F,
    0x13, 0x40, 0x5F,
    0x13, 0x60, 0x7F,
    0x14, 0x40, 0x5F,
    0x14, 0x60, 0x7F
}

tmpMatrix = [0x80, 0x01, 0x02, 0x83, 0x04, 0x85, 0x86, 0x07, 0x08, 0x89, 0x8a, 0x0b, 0x8c, 0x0d, 0x0e, 0x8f,
             0x10, 0x91, 0x92, 0x13, 0x94, 0x15, 0x16, 0x97, 0x98, 0x19, 0x1a, 0x9b, 0x1c, 0x9d, 0x9e, 0x1f,
             0x20, 0xa1, 0xa2, 0x23, 0xa4, 0x25, 0x26, 0xa7, 0xa8, 0x29, 0x2a, 0xab, 0x2c, 0xad, 0xae, 0x2f,
             0xb0, 0x31, 0x32, 0xb3, 0x34, 0xb5, 0xb6, 0x37, 0x38, 0xb9, 0xba, 0x3b, 0xbc, 0x3d, 0x3e, 0xbf,
             0x40, 0xc1, 0xc2, 0x43, 0xc4, 0x45, 0x46, 0xc7, 0xc8, 0x49, 0x4a, 0xcb, 0x4c, 0xcd, 0xce, 0x4f,
             0xd0, 0x51, 0x52, 0xd3, 0x54, 0xd5, 0xd6, 0x57, 0x58, 0xd9, 0xda, 0x5b, 0xdc, 0x5d, 0x5e, 0xdf,
             0xe0, 0x61, 0x62, 0xe3, 0x64, 0xe5, 0xe6, 0x67, 0x68, 0xe9, 0xea, 0x6b, 0xec, 0x6d, 0x6e, 0xef,
             0x70, 0xf1, 0xf2, 0x73, 0xf4, 0x75, 0x76, 0xf7, 0xf8, 0x79, 0x7a, 0xfb, 0x7c, 0xfd, 0xfe, 0x7f]

_specialChars = {
    0xb0: '®',
    0x31: '°',
    0x32: '½',
    0xb3: '¿',
    0xb4: '™',
    0xb5: '¢',
    0xb6: '£',
    0x37: '♪',
    0x38: 'à',
    0xb9: ' ',
    0xba: 'è',
    0x3b: 'â',
    0xbc: 'ê',
    0x3d: 'î',
    0x3e: 'ô',
    0xbf: 'û'
}

_extendedChars = {
    '9220': 'Á',
    '92a1': 'É',
    '92a2': 'Ó',
    '9223': 'Ú',
    '92a4': 'Ü',
    '9225': 'ü',
    '9226': '‘',
    '92a7': '¡',
    '92a8': '*',
    '9229': '’',
    '922a': '—',
    '92ab': '©',
    '922c': '℠',
    '92ad': '•',
    '92ae': '“',
    '922f': '”',
    '92b0': 'À',
    '9231': 'Â',
    '9232': 'Ç',
    '92b3': 'È',
    '9234': 'Ê',
    '92b5': 'Ë',
    '92b6': 'ë',
    '9237': 'Î',
    '9238': 'Ï',
    '92b9': 'ï',
    '92ba': 'Ô',
    '923b': 'Ù',
    '92bc': 'ù',
    '923d': 'Û',
    '923e': '«',
    '92bf': '»',
    '1320': 'Ã',
    '13a1': 'ã',
    '13a2': 'Í',
    '1323': 'Ì',
    '13a4': 'ì',
    '1325': 'Ò',
    '1326': 'ò',
    '13a7': 'Õ',
    '13a8': 'õ',
    '1329': '{',
    '132a': '}',
    '13ab': '\\',
    '132c': '^',
    '13ad': '_',
    '13ae': '¦',
    '132f': '~',
    '13b0': 'Ä',
    '1331': 'ä',
    '1332': 'Ö',
    '13b3': 'ö',
    '1334': 'ß',
    '13b5': '¥',
    '13b6': '¤',
    '1337': '|',
    '1338': 'Å',
    '13b9': 'å',
    '13ba': 'Ø',
    '133b': 'ø',
    '13bc': '┌',
    '133d': '┐',
    '133e': '└',
    '13bf': '┘',
}


class SCCItem(object):

    start_time = None
    end_time = None
    text = None


def _milliseconds_to_smtpe(time: int):

    hoursMs = int(time / 3600000) * 3600000
    minutesMs = int((time - hoursMs) / 60000) * 60000
    secondsMs = int((time - (hoursMs + minutesMs)) / 1000) * 1000
    millseconds = int(time - (hoursMs + minutesMs + secondsMs))

    return '{0:02d}:{1:02d}:{2:02d}.{3:03d}'.format(int(hoursMs / 3600000), int(minutesMs / 60000), int(secondsMs / 1000), int(millseconds))


def _debug_render_command(control_codes: str):

    command = None

    if control_codes[0] == 0x11:
        pass
        # if 0x20 <= control_codes[1] <= 0x2F:
        #    command = "MRC - Mid-row Code"
    elif control_codes[0] == 0x14:
        if control_codes[1] == 0x20:
            command = "RCL - Resume caption loading"
        elif control_codes[1] == 0x21:
            command = "RB - Backspace"
        elif control_codes[1] == 0x22:
            command = "AOF - Alarm Off"
        elif control_codes[1] == 0x23:
            command = "AON - Alarm On"
        elif control_codes[1] == 0x24:
            command = "DER - Delete to end of row"
        elif control_codes[1] == 0x25:
            command = "RU2 - Roll-up captions-2"
        elif control_codes[1] == 0x26:
            command = "RU3 - Roll-up captions-3"
        elif control_codes[1] == 0x27:
            command = "RU4 - Roll-up captions-4"
        elif control_codes[1] == 0x28:
            command = "FON - Flash On"
        elif control_codes[1] == 0x29:
            command = "RDC - Resume direct captioning"
        elif control_codes[1] == 0x2A:
            command = "TR  - Text restart"
        elif control_codes[1] == 0x2B:
            command = "RTD - Resume Text restart"
        elif control_codes[1] == 0x2C:
            command = "EDM - Erase Display Memory"
        elif control_codes[1] == 0x2D:
            command = "CR - Carriage Return"
        elif control_codes[1] == 0x2E:
            command = "ENM - Erase Non-Display Memory"
        elif control_codes[1] == 0x2F:
            command = "EOC - Erase Of Caption (flip-memory)"
        elif control_codes[1] == 0x21:
            command = "TO1 - Tab Offset 1 Column"
        elif control_codes[1] == 0x22:
            command = "TO1 - Tab Offset 2 Column"
        elif control_codes[1] == 0x23:
            command = "TO2 - Tab Offset 3 Column"

    if command:
        return command

    return command


def parse(file: str, logger: logging.Logger):

    for i in range(128):
        _ccTxMatrix[tmpMatrix[i]] = i

    fps = 30.00

    channelOne = False
    currentBuffer = ""
    italics = False

    last_cc_code1 = None
    last_cc_code2 = None

    items = []
    lastClear = None

    with open(file, 'r') as file:
        for line in file:
            if len(line.strip()) > 0:

                line = line.replace("\n", "")
                result = re.match("(.*)\t(.*)", line)

                if result:
                    critera = result.groups(1)[0]

                    smpteTokens = re.match("([0-9*]{2}):([0-9*]{2}):([0-9*]{2})[:;]*([0-9*]{2})", critera)

                    if smpteTokens:

                        #parse the line time 
                        time_stamp = smpteTokens.groups(1)
                        sampleTime = int(time_stamp[0]) * 3600 + int(time_stamp[1]) * 60 + int(time_stamp[2]) + (int(time_stamp[3]) / fps)

                        #create tokenzed list of control codes
                        tokens = result.groups(2)[1].split(' ')
                        
                        #create list of control coders  
                        codes = [f for f in tokens if len(f) > 0]

                        for sample in codes:

                            # convert hex control codes to a number
                            cc_raw_code1 = int(sample[0:2], 16)
                            cc_raw_code2 = int(sample[-2:], 16)

                            # conver raw control codes
                            cc_code1 = _ccTxMatrix[cc_raw_code1]
                            cc_code2 = _ccTxMatrix[cc_raw_code2]

                            # skip diplciate codes (this may not be ideal)
                            if (cc_raw_code1 == last_cc_code1 and cc_raw_code2 == last_cc_code2) or cc_code1 == 0x17:
                                continue
                                 
                            last_cc_code1 = cc_raw_code1
                            last_cc_code2 = cc_raw_code2

                            if lastClear is None:
                                lastClear = sampleTime

                            if cc_code1 == 0x11 and cc_raw_code2 in _specialChars:
                                cc_code2 = _specialChars[cc_raw_code2]

                            elif cc_code1 == 0x11 and cc_raw_code2 in _extendedChars:
                                cc_code2 = _extendedChars[cc_raw_code2]

                            if logger:
                                smpte = _milliseconds_to_smtpe(sampleTime * 1000)
                                cmd = _debug_render_command([cc_code1, cc_code2])

                                if cmd:
                                    logger.debug("[{0}] [{4}] [{1:02x}] [{2:02x}] [{3}]".format(smpte, cc_code1, cc_code2, cmd, sample))
                                else:
                                    try:
                                        logger.debug("[{0}] [{1}] [{2:002x}] [{3:002x}] [{4}] [{5}]".format(smpte, sample, cc_code1, cc_code2, chr(cc_code1), chr(cc_code2)))
                                    except:
                                        logger.debug("[{0}] [{4}] [{1}] [{2}] [{3}]".format(smpte, cc_code1, cc_code2, cmd, sample))

                            if 0x10 <= cc_code1 <= 0x14:

                                channelOne = True

                                if (cc_code1 == 0x14 and cc_code2 == 0x28) or (cc_code1 == 0x14 and cc_code2 == 0x72) or (cc_code1 == 0x14 and cc_code2 == 0x74) or (cc_code1 == 0x14 and cc_code2 == 0x70):
                                    if currentBuffer:
                                        currentBuffer += '\n'
                                elif cc_code1 == 0x11 and cc_code2 == 0x2e:
                                    if not italics:
                                        currentBuffer += "<i>"
                                        italics = True
                                elif cc_code1 == 0x11 and cc_raw_code2 in _specialChars:
                                    currentBuffer += cc_code2
                                elif cc_code1 == 0x12 and cc_raw_code2 in _extendedChars:
                                    currentBuffer += cc_code2
                                elif cc_code1 == 0x14 and (cc_code2 == 0x20 or cc_code2 == 0x26 or cc_code2 == 0x2f or cc_code2 == 0x2D or cc_code2 == 0x2F or cc_code2 == 0x2E):

                                    if italics:
                                        currentBuffer += "</i>"

                                    if currentBuffer:
                                        item = SCCItem()
                                        item.end_time = sampleTime * 1000
                                        item.start_time = lastClear * 1000
                                        item.text = currentBuffer
                                        items.append(item)

                                    currentBuffer = ""
                                    lastClear = sampleTime
                                    italics = False

                            elif 0x20 <= cc_code1 <= 0x7F and channelOne:

                                if currentBuffer == "":
                                    sampleTime = sampleTime

                                currentBuffer += chr(cc_code1)

                                if 0x20 <= cc_code2 <= 0x7F:
                                    currentBuffer += chr(cc_code2)

                            elif 0x18 <= cc_code1 <= 0x1F:
                                channelOne = False

    return items


def write_srt(items: SCCItem, output_file: str):

     with open(output_file, "w+") as f:
        for idx, val  in enumerate(items):
            f.write('{}\n'.format(str(idx + 1)))
            f.write('{} --> {}\n'.format(_milliseconds_to_smtpe(val.start_time), _milliseconds_to_smtpe(val.end_time)))
            f.write('{}\n'.format(val.text))
            f.write('\n')


if __name__ == "__main__":
    
    log_format='%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=log_format)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    logHandler = logging.StreamHandler(sys.stdout)
    logHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(log_format)
    logHandler.setFormatter(formatter)

    logger.addHandler(logHandler)

    items = parse("test.scc", logger)
    
    for item in items:
        print("[{}] [{}] [{}]".format(_milliseconds_to_smtpe(item.start_time), _milliseconds_to_smtpe(item.end_time), item.text))
    
    write_srt(items, "test.srt")
