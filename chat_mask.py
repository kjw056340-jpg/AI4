import re


def mask_bad_words(chat_message: str, bad_words: list[str]) -> str:
    # 원본을 글자 목록으로 복사하면 필요한 위치만 '*'로 바꿀 수 있습니다.
    masked_chars = list(chat_message)

    for word in bad_words:
        # 빈 금지어는 실제 글자가 없으므로 건너뜁니다.
        if not word:
            continue

        # 특수문자도 일반 글자로 찾고, 영어 대소문자는 구분하지 않습니다.
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        search_start = 0

        while True:
            # 항상 원본에서 검색해야 다른 금지어와 겹쳐도 찾을 수 있습니다.
            match = pattern.search(chat_message, search_start)
            if match is None:
                break

            # 찾은 구간의 각 글자를 별표 하나로 바꿉니다.
            for index in range(match.start(), match.end()):
                masked_chars[index] = '*'

            # 한 글자 뒤부터 다시 찾으면 서로 겹치는 같은 금지어도 찾습니다.
            search_start = match.start() + 1

    # 바뀐 글자 목록을 하나의 문자열로 합칩니다.
    return ''.join(masked_chars)


if __name__ == '__main__':
    # 기본 동작과 문장 구조 보존
    assert mask_bad_words('너는 바보야!', ['바보']) == '너는 **야!'
    assert mask_bad_words('BAD Bad bad', ['bad']) == '*** *** ***'
    assert mask_bad_words('bad BAD', ['BaD']) == '*** ***'
    assert mask_bad_words('바보, 멍청이!', ['바보', '멍청이']) == '**, ***!'
    assert mask_bad_words('안녕, 친구!', ['바보']) == '안녕, 친구!'
    assert mask_bad_words('  BAD\t바보\n끝!  ', ['bad', '바보']) == '  ***\t**\n끝!  '

    # 빈 입력, 빈 금지어, 중복 금지어
    assert mask_bad_words('', ['bad']) == ''
    assert mask_bad_words('hello', []) == 'hello'
    assert mask_bad_words('', []) == ''
    assert mask_bad_words('hello', ['']) == 'hello'
    assert mask_bad_words('bad', ['', 'bad']) == '***'
    assert mask_bad_words('bad', ['bad', 'bad']) == '***'

    # 반복, 겹침, 목록 순서, 단어 내부의 부분 문자열
    assert mask_bad_words('바보바보', ['바보']) == '****'
    assert mask_bad_words('ababa', ['aba']) == '*****'
    assert mask_bad_words('abcde', ['abc', 'cde']) == '*****'
    assert mask_bad_words('abcde', ['cde', 'abc']) == '*****'
    assert mask_bad_words('badly', ['bad']) == '***ly'
    assert mask_bad_words('a', ['longword']) == 'a'

    # 정규식 특수문자도 문자 그대로 처리
    assert mask_bad_words('a.b axb', ['a.b']) == '*** axb'
    assert mask_bad_words('C++ [bad] (bad)', ['c++', '[bad]']) == '*** ***** (bad)'
    assert mask_bad_words('a*b?', ['*', '?']) == 'a*b*'
    assert mask_bad_words('a\\b', ['\\']) == 'a*b'

    # 공백과 이모지를 포함한 금지어, 유니코드 대소문자
    assert mask_bad_words('not good!', ['not good']) == '********!'
    assert mask_bad_words('안녕😀😀!', ['😀']) == '안녕**!'
    assert mask_bad_words('Ä ä', ['ä']) == '* *'

    # 입력 목록을 변경하지 않고 결과의 길이를 유지
    words = ['bad', '바보']
    message = 'BAD와 바보!'
    assert mask_bad_words(message, words) == '***와 **!'
    assert words == ['bad', '바보']
    assert message == 'BAD와 바보!'
    assert len(mask_bad_words(message, words)) == len(message)

    print('모든 assert 테스트를 통과했습니다.')
