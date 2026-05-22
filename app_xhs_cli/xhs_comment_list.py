import time
from util import *
def comment_list(driver,target_count,max_swipe_count=10):
    collected = []  # 存放评论数据
    identifier_ary = []  # 用标题来去重
    swipe_count = 0
    while len(collected) < target_count:
        # 获得评论卡片,左边界为必须为0,否则可能是回复
        linear_layout_all= element_located_all(5, (AppiumBy.XPATH, "//android.widget.LinearLayout[@index=0 "
                                                           "and substring-before(substring-after(@bounds, '['), ',') = '0' "
                                                           "and count(child::*) = 2 "
                                                           "and child::*[1][self::android.view.ViewGroup] "
                                                           "and child::*[2][self::android.widget.LinearLayout] "
                                                           "]"))

        if linear_layout_all:
          # print(f"linear_layout_all:{len(linear_layout_all)}")
          for ele in  linear_layout_all:
               child_layout=ele.find_element(AppiumBy.XPATH, "//self::android.widget.LinearLayout[1]")
               if child_layout:
                    text_views= child_layout.find_elements(AppiumBy.XPATH, "//android.widget.TextView")
                    # 我需要完整的评论内容,包括四个元素
                    if len(text_views)==4:
                       nick_name=text_views[0].text
                       content=text_views[1].text
                       date=text_views[2].text.replace("回复","")
                       like_num=text_views[3].text
                       like_num= "0" if like_num=="  " else like_num
                       identifier=nick_name+"|"+content
                       # print(f"nick_name:{nick_name} content:{content} date_and_lbs:{date} like_num:{like_num}")
                       if identifier in identifier_ary:
                           continue
                       identifier_ary.append(identifier)
                       collected.append({
                           "nick_name":nick_name,
                           "content":content,
                           "date_and_lbs":date,
                           "like_num":like_num
                       })
                       if len(collected) >= target_count:
                           return collected

        # 超过最大滚动次数退出
        if  swipe_count>=max_swipe_count:
            break
        scroll_small_step(driver,0.2)
        swipe_count=swipe_count+1

    return collected


# python openappcli.py xhs-comment-list --note_id "6a0a94d4000000003601ec7a" --note_type normal --limit 10
# python openappcli.py xhs-comment-list --note_id "6a0d3b07000000003601f3b2" --note_type normal --limit 10
# python openappcli.py xhs-comment-list --note_id "69c3eed8000000001a02107b" --note_type video --limit 10
# python openappcli.py xhs-comment-list --note_id "699982ec000000001a02bc1a" --note_type video --limit 10
def run(args):
    start_time = time.time()
    comment_node = {"note_id":f"{args.note_id}","comment_sum": "0", "comment_list": []}
    try:
        driver = get_driver()
        deep_link_url = f"xhsdiscover://item/{args.note_id}?type={args.note_type}"
        driver.execute_script('mobile: deepLink', {'url': f'{deep_link_url}', })
        # 点击评论
        if element_on_clickable(3, (AppiumBy.XPATH, "//android.widget.Button[(@index=3 or @index=2) and contains(@content-desc, '评论')]")):
            text_view=element_located(5, (AppiumBy.XPATH, "//android.widget.TextView[@index=0 "
                                                          "and contains(@text, '条评论') "
                                                          "and ( parent::android.widget.RelativeLayout[@index=1] or parent::android.view.ViewGroup[@index=0] ) "
                                                          "]"),False)
            if text_view:
              comment_node["note_id"] = args.note_id
              comment_node["comment_sum"]=text_view.text
              comment_node["comment_list"]=comment_list(driver,args.limit,args.limit)



    except Exception as e:
        print(f"run错误: {e}")
        sys.exit(2)
    print(json.dumps(comment_node, ensure_ascii=False, indent=2))
    elapsed = time.time() - start_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"读取条{len(comment_node["comment_list"])}条评论 总耗时: {int(hours):02d}:{int(minutes):02d}:{seconds:05.2f}")


