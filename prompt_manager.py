"""나만의 프롬프트 관리 프로그램.

터미널에서 메뉴 번호를 입력해 프롬프트를 추가/조회/검색/관리하는 콘솔 프로그램이다.
표준 라이브러리만 사용한다.
"""

import sys

# 윈도우 콘솔에서 한글과 이모지(⭐)가 깨지지 않도록 출력 인코딩을 UTF-8로 맞춘다.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass


# 미리 정의된 카테고리 목록
CATEGORIES = ["텍스트 생성", "이미지 생성", "영상 생성", "페르소나", "자동화", "기타"]

# 화면 구분선
LINE = "─" * 40


def make_prompt(title, content, category, favorite=False):
    """프롬프트 한 개(딕셔너리)를 만들어 돌려준다."""
    return {
        "title": title,
        "content": content,
        "category": category,
        "favorite": favorite,
    }


def load_default_prompts():
    """이전 미션에서 작성한 프롬프트를 기본 데이터로 돌려준다."""
    return [
        make_prompt(
            "블로그 글 작성 도우미",
            "당신은 10년 경력의 전문 블로거입니다.\n"
            "주어진 주제에 대해 SEO에 최적화된 블로그 글을 작성해주세요.\n"
            "서론, 본론, 결론 구조를 갖추고,\n"
            "독자의 관심을 끄는 제목을 3개 제안해주세요.",
            "텍스트 생성",
            favorite=True,
        ),
        make_prompt(
            "제품 썸네일 생성",
            "다음 제품의 매력적인 썸네일 이미지를 생성해주세요.\n"
            "제품: {제품명}\n"
            "스타일: 미니멀, 파스텔 톤 배경, 부드러운 그림자\n"
            "구도: 정면 45도, 여백을 넉넉히 두고 중앙 배치\n"
            "비율: 1:1 (정사각형)",
            "이미지 생성",
        ),
        make_prompt(
            "IT 컨설턴트 페르소나",
            "당신은 15년 경력의 IT 컨설턴트입니다.\n"
            "고객의 상황을 먼저 3가지 질문으로 파악한 뒤,\n"
            "현실적인 대안 2~3가지를 장단점과 함께 제시하세요.\n"
            "전문 용어는 반드시 한 줄 설명을 덧붙여 주세요.",
            "페르소나",
        ),
        make_prompt(
            "뉴스 요약 프롬프트",
            "아래 기사 본문을 읽고 다음 형식으로 요약해주세요.\n"
            "1) 한 줄 요약\n"
            "2) 핵심 내용 3가지 (불릿)\n"
            "3) 이 소식이 중요한 이유\n"
            "추측은 쓰지 말고 기사에 있는 사실만 사용하세요.",
            "자동화",
        ),
        make_prompt(
            "광고 스크립트 작성",
            "30초 분량의 숏폼 광고 영상 스크립트를 작성해주세요.\n"
            "제품: {제품명}, 타깃: {타깃 고객}\n"
            "구성: 0~3초 후킹 문구, 4~20초 핵심 benefit 3가지, 21~30초 CTA\n"
            "각 장면마다 화면 설명과 나레이션을 나눠서 표기해주세요.",
            "영상 생성",
        ),
    ]


def input_nonempty(message):
    """비어 있지 않은 값을 입력받을 때까지 다시 물어본다."""
    while True:
        value = input(message).strip()
        if value:
            return value
        print("값이 비어 있습니다. 다시 입력해주세요.")


def choose_category():
    """카테고리를 번호로 고르거나 직접 입력받아 돌려준다."""
    print("\n카테고리 선택:")
    for number, category in enumerate(CATEGORIES, start=1):
        print(f"{number}) {category}")
    print(f"{len(CATEGORIES) + 1}) 직접 입력")

    while True:
        choice = input("선택: ").strip()
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(CATEGORIES):
                return CATEGORIES[index - 1]
            if index == len(CATEGORIES) + 1:
                return input_nonempty("카테고리 직접 입력: ")
        print("잘못된 번호입니다. 목록에 있는 번호를 입력해주세요.")


def add_prompt(prompts):
    """새 프롬프트를 입력받아 목록에 추가한다."""
    print("\n=== 프롬프트 추가 ===")
    title = input_nonempty("제목: ")
    content = input_nonempty("내용: ")
    category = choose_category()

    prompts.append(make_prompt(title, content, category))
    print(f"\n'{title}' 프롬프트가 추가되었습니다!")


def format_prompt_line(number, prompt):
    """목록 한 줄을 '번호. [카테고리] 제목 ⭐' 형태의 문자열로 만든다."""
    star = " ⭐" if prompt["favorite"] else ""
    return f"{number}. [{prompt['category']}] {prompt['title']}{star}"


def print_prompt_list(prompts, empty_message="등록된 프롬프트가 없습니다."):
    """프롬프트 목록을 번호와 함께 출력한다. 비어 있으면 안내 문구를 보여준다."""
    if not prompts:
        print(empty_message)
        return

    for number, prompt in enumerate(prompts, start=1):
        print(format_prompt_line(number, prompt))
    print(f"\n총 {len(prompts)}개의 프롬프트")


def show_list(prompts):
    """저장된 모든 프롬프트를 출력한다."""
    print("\n=== 프롬프트 목록 ===")
    print_prompt_list(prompts)


def show_menu():
    """메인 메뉴를 화면에 출력한다."""
    print()
    print("=== 나만의 프롬프트 관리 ===")
    print("1. 프롬프트 추가")
    print("2. 프롬프트 목록")
    print("3. 카테고리별 조회")
    print("4. 프롬프트 검색")
    print("5. 프롬프트 상세 보기")
    print("6. 즐겨찾기 관리")
    print("7. 즐겨찾기 목록")
    print("0. 종료")


def main():
    """프로그램의 시작점. 메뉴를 반복해서 보여주고 기능을 실행한다."""
    prompts = load_default_prompts()
    print(f"기본 프롬프트 {len(prompts)}개를 불러왔습니다.")

    while True:
        show_menu()
        choice = input("선택: ").strip()

        if choice == "0":
            print("프로그램을 종료합니다. 안녕히 가세요!")
            break
        elif choice == "1":
            add_prompt(prompts)
        elif choice == "2":
            show_list(prompts)
        elif choice in ("3", "4", "5", "6", "7"):
            print("아직 준비 중인 기능입니다.")
        else:
            print("잘못된 번호입니다. 메뉴에 있는 번호를 입력해주세요.")


if __name__ == "__main__":
    main()
