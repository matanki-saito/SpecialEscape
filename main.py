import argparse

escape_targets = [
    0xA4,
    0xA3,
    0xA7,
    0x24,
    0x5B,
    0x00,
    0x5C,
    0x20,
    0x0D,
    0x0A,
    0x22,
    0x7B,
    0x7D,
    0x40,
    0x3B,
    0x80,
    0x7E,
    0xBD,
    0x5F
]


def encoder(src_array):
    """
    変換器
    :param src_array: Unicodeコードポイント配列
    :return:変換後の配列
    """

    result = []
    for code_point in src_array:

        # BMP外の文字
        if code_point > 0xFFFF:
            print("変換できない文字")
            continue

        # null文字
        if code_point == 0:
            print("null文字がある")
            continue

        high_byte = (code_point >> 8) & 0x000000FF
        low_byte = code_point & 0x000000FF

        # 2byteじゃない
        if high_byte is 0:
            result.append(code_point)
            continue

        escape_char = 0x10

        if high_byte in escape_targets:
            escape_char += 2

        if low_byte in escape_targets:
            escape_char += 1

        if escape_char is 0x11:
            low_byte += 15
        elif escape_char is 0x12:
            high_byte -= 9
        elif escape_char is 0x13:
            low_byte += 15
            high_byte -= 9
        else:
            pass

        result.append(escape_char)
        result.append(low_byte)
        result.append(high_byte)

    return result


def main(params):
    with open(params.src, "rt", encoding="utf-8") as fr:
        unicode_codepoint_array = map(ord, fr.read())
        escaped_unicode_codepoint_array = encoder(unicode_codepoint_array)

        with open(params.dest, "wt", encoding="utf-8") as fw:
            text = "".join(map(chr, escaped_unicode_codepoint_array))
            fw.write(text)


def generate_default_arg_parser():
    """
    argumentsパーサーを作成
    :return: パーサー
    """

    # title
    result = argparse.ArgumentParser(
        description='Process some integers.'
    )

    # ソース
    result.add_argument(
        'src',
        metavar='src',
        type=str,
        help='source file or directory.')

    # 出力先
    result.add_argument(
        '-out',
        metavar='X',
        dest='dest',
        default="test.txt",
        help='output directory')

    # タイプ
    result.add_argument(
        '-type',
        metavar='X',
        dest='type',
        default="eu4",
        help='eu4 or ck2')

    return result


if __name__ == '__main__':
    parser = generate_default_arg_parser()
    main(parser.parse_args())
