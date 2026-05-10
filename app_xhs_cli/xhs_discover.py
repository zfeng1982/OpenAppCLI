from .xhs_common import *

def run(args):
    driver = get_driver()
    result = {}
    try:

        notes = collect_note_cards(driver, args.limit)
        print(f"notes len:{len(notes)}")
        result["notes"] = notes

    except Exception as e:
        print(f"状态: - 未创建 ({e})")
    print(json.dumps(result, ensure_ascii=False, indent=2))