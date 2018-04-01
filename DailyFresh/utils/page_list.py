def get_page_list(total_page, pindex):
    page_list = []
    if total_page < 5:
        page_list = range(1, total_page + 1)
    elif pindex <= 2:
        page_list = range(1, 6)
    elif pindex >= total_page - 1:
        page_list = range(total_page - 4, total_page + 1)
    else:
        page_list = range(pindex - 2, pindex + 3)
    return page_list