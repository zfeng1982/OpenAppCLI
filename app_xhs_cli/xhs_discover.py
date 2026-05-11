from .xhs_common import *
# python openappcli.py xhs-discover  --limit 2
def run(args):
    driver = get_driver()
    result = {}
    notes=[]
    try:
        notes = collect_note_index_cards(driver, args.limit,15)
        result["notes"] = notes
    except Exception as e:
        print(f"({e})")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"notes len:{len(notes)}")