def filter_title(title):
    # word must be in title
    contain = False
    if '减持' in title:
        contain = True
        if '完成' in title:    # if contain both words, must be right
            return True

    # words that should not be in title
    exclude_list = ['误操作', '倡议书', '进展', '核查意见', '补充', '计划' ]
    for w in exclude_list:
        if w in title:
            return False

    return contain


def filter_title(title):
    # word must be in title
    contain = False
    if '减持' in title:
        contain = True
        if '完成' in title or '完毕' in title:    # if contain both words, must be right
            return True

    # words that should not be in title
    exclude_list = ['提示', '终止', '误操作', '倡议书', '进展', '核查意见', '补充', '计划' ]
    for w in exclude_list:
        if w in title:
            return False

    return contain

# 关于接待机构调研情况的公告
# 2017年5月机构投资者调研记录/纪要
# 调研活动附件之公司情况介绍
# 2017年6月7日调研活动附件之演示文稿
# 2017年6月6日投资者关系活动记录表

def filter_title(title):
    # word must be in title
    if '预增' in title:
        return True
    else:
        return False
    
def filter_title(title):
    # word must be in title
    contain = False
    if '扭亏' in title:
        contain = True

    # words that should not be in title
    exclude_list = ['补充']
    for w in exclude_list:
        if w in title:
            return False

    return contain

