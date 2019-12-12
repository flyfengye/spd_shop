import requests as _requests
# from bs4 import BeautifulSoup
import re
import json


class Spider:
    def __init__(self):
        pass

    def start(self):
        src_url = 'https://www.sephora.cn/category/230151-60001/page%d/' \
            '?hasInventory=0' \
            '&sortField=1' \
            '&sortMode=desc'
        src_url = 'https://www.sephora.cn/category/60171-60001/page%d/u60250/' \
                  '?hasInventory=0&sortField=1&sortMode=desc'
        # src_url = 'https://www.sephora.cn/function/?cat=60001-60005&fun=保湿补水&attr=功效&hasInventory=0' \
        #           '&sortField=1&sortMode=desc&currentPage=%d&filters='
        count = 0

        for page_nbr in range(1, 60):
            url = src_url.format(page_nbr)
            res = self.request_get(url)
            content = res.content
            # soup = BeautifulSoup(content, 'html.parser')

            html = content.decode('utf-8')
            with open('./aa.html', 'w', encoding='utf-8') as f:
                f.write(html)
            mat_obj = re.search('window.__INITIAL_STATE__ = (.*?)window.__INITIAL_ENV__ =', html, re.S)
            if not mat_obj:
                raise Exception('mat_obj')

            res_dict = json.loads(mat_obj.group(1).strip().rstrip(';'))
            data_list = res_dict['mainContent']['results']['content']

            for data in data_list:
                count += 1

                title_cn = data['productCN']
                # brand_cn = data['brandCN']
                # brand_en = data['brandEN']
                max_price = data['maxDiscountPrice']
                min_price = data['minDiscountPrice']
                has_inventory = data['hasInventory']
                if max_price:
                    price = f'{min_price}~￥{max_price}'
                else:
                    price = min_price

                # print(f'{count}. 品牌: {brand_cn} {brand_en}  商品: {title_cn}  价格: ￥{price}')
                print(f'{count}. 商品: {title_cn}  价格: ￥{price}  库存: {"有" if has_inventory else "无"}')

    @staticmethod
    def request_get(url):
        #print('GET', url)
        try:
            res = _requests.get(url, headers={}, timeout=20)
        except Exception as e:
            print(e)
            return
        if res.status_code == 200:
            return res
        else:
            print(res.status_code)
            print(res.text)


if __name__ == '__main__':
    spider = Spider()
    spider.start()
