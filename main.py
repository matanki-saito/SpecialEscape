import argparse
import os
import pathlib

eu4_escape_targets = [
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

ck2_escape_targets = [
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


def generate_encoder(escape_targets, high_byte_shift, low_byte_shift):
    """
    変換器生成
    :param escape_targets: エスケープ対象のコードポイント配列
    :param low_byte_shift: 下位バイトシフト数
    :param high_byte_shift 上位バイトシフト数
    :return:変換後の配列
    """

    def __(src_array):
        """
        変換器
        :param src_array: コードポイント配列
        :return:
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
                low_byte = low_byte + low_byte_shift
            elif escape_char is 0x12:
                high_byte = high_byte + high_byte_shift
            elif escape_char is 0x13:
                low_byte = low_byte + low_byte_shift
                high_byte = high_byte + high_byte_shift
            else:
                pass

            result.append(escape_char)
            result.append(low_byte)
            result.append(high_byte)

        return result

    return __


def target_is_directory(params, encoder):
    is_out_dir = os.path.isdir(str(params.out))

    # 走査
    for file_path in pathlib.Path(params.src).glob('**/*.txt'):

        # 指定がない場合は、ソースと同じ場所に、同じ名前で拡張子を.encodedにしたものを保存する
        if params.out is None:
            out_file_path = os.path.join(
                os.path.dirname(os.path.abspath(str(file_path))),
                os.path.basename(str(file_path)) + ".utf8"
            )

        # 出力先が存在するディレクトリ
        elif is_out_dir:
            out_file_path = os.path.join(
                str(params.out),
                str(file_path).replace(str(params.src) + "\\", "")
            )

            dir_path = os.path.dirname(str(out_file_path))
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

        else:
            raise Exception("出力先が不正")

        do_file(in_file_path=file_path,
                out_file_path=out_file_path,
                encoder=encoder)


def target_is_file(params, encoder):
    # 指定がない場合は、ソースと同じ場所に、同じ名前で拡張子を.utf8にしたものを保存する
    if params.out is None:
        out_file_path = os.path.join(
            os.path.dirname(os.path.abspath(params.src)),
            os.path.basename(params.src) + ".utf8"
        )

    # 指定先が存在するディレクトリの場合は、そこに同じ名前で保存する
    elif os.path.isdir(params.out):
        out_file_path = os.path.join(
            params.out,
            os.path.basename(params.src)
        )

    # 指定先がフルパス
    elif params.out is not "":
        out_file_path = params.out
    else:
        raise Exception("出力先が不正")

    do_file(in_file_path=params.src,
            out_file_path=out_file_path,
            encoder=encoder)


def do_file(in_file_path, out_file_path, encoder):
    """
    ファイルを変換
    :param in_file_path: 入力先ファイルパス
    :param out_file_path: 出力先ファイルパス
    :param encoder: エンコーダー
    :return:
    """

    # 読み込み
    with open(in_file_path, "rt", encoding="utf-8") as fr:
        # 変換
        escaped_unicode_codepoint_array = encoder(src_array=map(ord, fr.read()))

        # 保存
        with open(out_file_path, "wt", encoding="utf-8") as fw:
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
        dest='out',
        help='output directory')

    # タイプ
    result.add_argument(
        '-type',
        metavar='X',
        dest='type',
        default="eu4",
        help='eu4 or ck2')

    return result


def main():
    """
    main
    :return:
    """

    parser = generate_default_arg_parser()
    params = parser.parse_args()

    # encoderを作る
    if params.type is "eu4":
        encoder = generate_encoder(
            escape_targets=eu4_escape_targets,
            high_byte_shift=-9,
            low_byte_shift=15)
    elif params.type is "ck2":
        encoder = generate_encoder(
            escape_targets=ck2_escape_targets,
            high_byte_shift=-9,
            low_byte_shift=16)
    else:
        raise Exception("typeが不明")

    # fileかdirか
    if os.path.isfile(params.src):
        target_is_file(params=params,
                       encoder=encoder)
    elif os.path.isdir(params.src):
        target_is_directory(params=params,
                            encoder=encoder)
    else:
        raise Exception("srcがみつからない")


if __name__ == '__main__':
    """
    entry-point
    """
    main()
