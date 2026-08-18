"""나만의 프롬프트 관리 프로그램.

터미널에서 메뉴 번호를 입력해 프롬프트를 추가/조회/검색/관리하는 콘솔 프로그램이다.
표준 라이브러리만 사용한다.
"""

import json
import os
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

# 보너스 기능에서 사용하는 파일 이름
DATA_FILE = "prompts.json"
EXPORT_DIR = "export"


def make_prompt(title, content, category, favorite=False):
    """프롬프트 한 개(딕셔너리)를 만들어 돌려준다."""
    return {
        "title": title,
        "content": content,
        "category": category,
        "favorite": favorite,
        "views": 0,  # 상세 보기 횟수 (보너스)
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


def normalize_title(title):
    """제목을 비교하기 좋게 다듬는다. (앞뒤/중복 공백 제거, 대소문자 무시)"""
    return " ".join(title.split()).lower()


def find_duplicate_title(prompts, title, skip_index=None):
    """같은 제목을 가진 프롬프트의 위치를 찾는다. 없으면 None을 돌려준다."""
    target = normalize_title(title)
    for index, prompt in enumerate(prompts):
        if index == skip_index:  # 수정할 때 자기 자신은 건너뛴다
            continue
        if normalize_title(prompt["title"]) == target:
            return index
    return None


def make_unique_title(prompts, title, skip_index=None):
    """제목 뒤에 (2), (3) ... 을 붙여 겹치지 않는 제목을 만든다."""
    number = 2
    while find_duplicate_title(prompts, f"{title} ({number})", skip_index) is not None:
        number += 1
    return f"{title} ({number})"


def resolve_duplicate_title(prompts, title, skip_index=None):
    """제목이 겹치면 어떻게 할지 물어본다. 취소를 고르면 None을 돌려준다."""
    while True:
        index = find_duplicate_title(prompts, title, skip_index)
        if index is None:
            return title

        print(f"\n[알림] 같은 제목이 이미 있습니다 "
              f"-> {format_prompt_line(index + 1, prompts[index])}")
        print("1) 다른 제목으로 다시 입력")
        print("2) 뒤에 번호를 붙여 저장 (예: 제목 (2))")
        print("0) 취소")

        choice = input("선택: ").strip()
        if choice == "1":
            title = input_nonempty("새 제목: ")
        elif choice == "2":
            return make_unique_title(prompts, title, skip_index)
        elif choice == "0":
            return None
        else:
            print("잘못된 번호입니다. 0, 1, 2 중에서 선택해주세요.")


def add_prompt(prompts):
    """새 프롬프트를 입력받아 목록에 추가한다."""
    print("\n=== 프롬프트 추가 ===")
    title = input_nonempty("제목: ")
    title = resolve_duplicate_title(prompts, title)
    if title is None:
        print("프롬프트 추가를 취소했습니다.")
        return

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


def collect_categories(prompts):
    """미리 정의된 카테고리에 직접 입력된 카테고리를 더해서 돌려준다."""
    categories = list(CATEGORIES)
    for prompt in prompts:
        if prompt["category"] not in categories:
            categories.append(prompt["category"])
    return categories


def show_by_category(prompts):
    """카테고리를 고르면 해당 카테고리의 프롬프트만 출력한다."""
    print("\n=== 카테고리별 조회 ===")
    categories = collect_categories(prompts)
    for number, category in enumerate(categories, start=1):
        print(f"{number}) {category}")

    choice = input("선택: ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(categories):
        print("잘못된 번호입니다. 목록에 있는 번호를 입력해주세요.")
        return

    selected = categories[int(choice) - 1]
    found = [p for p in prompts if p["category"] == selected]

    print(f"\n[{selected}] 카테고리 프롬프트:")
    print_prompt_list(found, f"[{selected}] 카테고리에는 등록된 프롬프트가 없습니다.")


def search_prompt(prompts):
    """제목이나 내용에 검색어가 들어 있는 프롬프트를 찾아서 출력한다."""
    print("\n=== 프롬프트 검색 ===")
    keyword = input_nonempty("검색어: ").lower()

    found = []
    for prompt in prompts:
        if keyword in prompt["title"].lower() or keyword in prompt["content"].lower():
            found.append(prompt)

    print("\n검색 결과:")
    print_prompt_list(found, "검색 결과가 없습니다.")


def select_prompt_index(prompts, message="번호 입력: "):
    """번호를 입력받아 리스트 인덱스로 바꿔 준다. 잘못된 입력이면 None을 돌려준다."""
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return None

    choice = input(message).strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(prompts):
        print("잘못된 번호입니다. 1 ~ %d 사이의 번호를 입력해주세요." % len(prompts))
        return None
    return int(choice) - 1


def show_detail(prompts):
    """번호로 고른 프롬프트의 전체 내용을 출력한다."""
    print("\n=== 프롬프트 상세 보기 ===")
    index = select_prompt_index(prompts)
    if index is None:
        return

    prompt = prompts[index]
    prompt["views"] = prompt.get("views", 0) + 1  # 조회수 기록 (보너스)

    print()
    print(LINE)
    print(f"제목: {prompt['title']}")
    print(f"카테고리: {prompt['category']}")
    print(f"즐겨찾기: {'⭐' if prompt['favorite'] else '없음'}")
    print(f"조회수: {prompt['views']}회")
    print(LINE)
    print("내용:")
    print(prompt["content"])
    print(LINE)


def toggle_favorite(prompts):
    """번호로 고른 프롬프트의 즐겨찾기를 추가하거나 해제한다."""
    print("\n=== 즐겨찾기 관리 ===")
    print_prompt_list(prompts)
    if not prompts:
        return

    index = select_prompt_index(prompts, "\n프롬프트 번호 입력: ")
    if index is None:
        return

    prompt = prompts[index]
    prompt["favorite"] = not prompt["favorite"]

    if prompt["favorite"]:
        print(f"'{prompt['title']}' 프롬프트를 즐겨찾기에 추가했습니다!")
    else:
        print(f"'{prompt['title']}' 프롬프트를 즐겨찾기에서 해제했습니다.")


def show_favorites(prompts):
    """즐겨찾기로 표시한 프롬프트만 모아서 출력한다."""
    print("\n=== 즐겨찾기 목록 ===")
    favorites = [p for p in prompts if p["favorite"]]
    print_prompt_list(favorites, "즐겨찾기한 프롬프트가 없습니다.")


def edit_prompt(prompts):
    """번호로 고른 프롬프트의 제목/내용/카테고리를 수정한다. (보너스)"""
    print("\n=== 프롬프트 수정 ===")
    print_prompt_list(prompts)
    if not prompts:
        return

    index = select_prompt_index(prompts, "\n수정할 프롬프트 번호: ")
    if index is None:
        return

    prompt = prompts[index]
    print("\n(그냥 엔터를 누르면 기존 값을 그대로 둔다)")

    title = input(f"제목 [{prompt['title']}]: ").strip()
    if title:
        title = resolve_duplicate_title(prompts, title, skip_index=index)
        if title is None:
            print("수정을 취소했습니다.")
            return
        prompt["title"] = title

    content = input("내용 (수정할 내용 입력): ").strip()
    if content:
        prompt["content"] = content

    answer = input(f"카테고리를 바꾸시겠습니까? 현재 [{prompt['category']}] (y/n): ").strip()
    if answer.lower() == "y":
        prompt["category"] = choose_category()

    print(f"\n'{prompt['title']}' 프롬프트를 수정했습니다!")


def delete_prompt(prompts):
    """번호로 고른 프롬프트를 목록에서 삭제한다. (보너스)"""
    print("\n=== 프롬프트 삭제 ===")
    print_prompt_list(prompts)
    if not prompts:
        return

    index = select_prompt_index(prompts, "\n삭제할 프롬프트 번호: ")
    if index is None:
        return

    title = prompts[index]["title"]
    answer = input(f"'{title}' 프롬프트를 정말 삭제할까요? (y/n): ").strip()
    if answer.lower() != "y":
        print("삭제를 취소했습니다.")
        return

    prompts.pop(index)
    print(f"'{title}' 프롬프트를 삭제했습니다.")


def show_top_prompts(prompts, top_n=5):
    """조회수가 높은 순으로 프롬프트를 정렬해서 출력한다. (보너스)"""
    print(f"\n=== 인기 프롬프트 Top {top_n} ===")
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return

    ranked = sorted(prompts, key=lambda p: p.get("views", 0), reverse=True)
    for number, prompt in enumerate(ranked[:top_n], start=1):
        star = " ⭐" if prompt["favorite"] else ""
        print(f"{number}. [{prompt['category']}] {prompt['title']}{star} "
              f"- 조회수 {prompt.get('views', 0)}회")


def save_to_json(prompts):
    """현재 프롬프트 목록을 JSON 파일로 저장한다. (보너스)"""
    print("\n=== JSON 파일로 저장 ===")
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"저장에 실패했습니다: {error}")
        return

    print(f"프롬프트 {len(prompts)}개를 '{DATA_FILE}' 파일에 저장했습니다.")


def load_from_json(prompts):
    """JSON 파일에서 프롬프트를 불러와 현재 목록을 교체한다. (보너스)"""
    print("\n=== JSON 파일에서 불러오기 ===")
    if not os.path.exists(DATA_FILE):
        print(f"'{DATA_FILE}' 파일이 없습니다. 먼저 저장해주세요.")
        return

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
    except (OSError, json.JSONDecodeError) as error:
        print(f"불러오기에 실패했습니다: {error}")
        return

    prompts.clear()
    for item in loaded:
        prompts.append(
            make_prompt(
                item.get("title", "제목 없음"),
                item.get("content", ""),
                item.get("category", "기타"),
                item.get("favorite", False),
            )
        )
        prompts[-1]["views"] = item.get("views", 0)

    print(f"프롬프트 {len(prompts)}개를 불러왔습니다.")


def make_markdown(category, prompts):
    """한 카테고리의 프롬프트들을 Markdown 문자열로 만든다. (보너스)"""
    lines = [f"# {category}", ""]
    for prompt in prompts:
        star = " ⭐" if prompt["favorite"] else ""
        lines.append(f"## {prompt['title']}{star}")
        lines.append("")
        lines.append("```")
        lines.append(prompt["content"])
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def export_markdown(prompts):
    """카테고리별로 Markdown 파일을 만들어 export 폴더에 저장한다. (보너스)"""
    print("\n=== 카테고리별 Markdown 내보내기 ===")
    if not prompts:
        print("내보낼 프롬프트가 없습니다.")
        return

    try:
        os.makedirs(EXPORT_DIR, exist_ok=True)
    except OSError as error:
        print(f"폴더를 만들지 못했습니다: {error}")
        return

    saved = 0
    for category in collect_categories(prompts):
        items = [p for p in prompts if p["category"] == category]
        if not items:
            continue

        filename = os.path.join(EXPORT_DIR, category.replace(" ", "_") + ".md")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(make_markdown(category, items))
        except OSError as error:
            print(f"'{filename}' 저장 실패: {error}")
            continue

        print(f"- {filename} ({len(items)}개)")
        saved += 1

    print(f"\n총 {saved}개의 Markdown 파일을 만들었습니다.")


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
    print("--- 보너스 기능 ---")
    print("8. 프롬프트 수정")
    print("9. 프롬프트 삭제")
    print("10. 인기 프롬프트 (조회수 Top)")
    print("11. JSON 파일로 저장")
    print("12. JSON 파일에서 불러오기")
    print("13. 카테고리별 Markdown 내보내기")
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
        elif choice == "3":
            show_by_category(prompts)
        elif choice == "4":
            search_prompt(prompts)
        elif choice == "5":
            show_detail(prompts)
        elif choice == "6":
            toggle_favorite(prompts)
        elif choice == "7":
            show_favorites(prompts)
        elif choice == "8":
            edit_prompt(prompts)
        elif choice == "9":
            delete_prompt(prompts)
        elif choice == "10":
            show_top_prompts(prompts)
        elif choice == "11":
            save_to_json(prompts)
        elif choice == "12":
            load_from_json(prompts)
        elif choice == "13":
            export_markdown(prompts)
        else:
            print("잘못된 번호입니다. 메뉴에 있는 번호를 입력해주세요.")


if __name__ == "__main__":
    main()
