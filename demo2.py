import requests as _requests
# from bs4 import BeautifulSoup
import re
import json
import os
import time
import random

DESKTOP_PATH = os.path.join(os.path.expanduser('~'), "Desktop")


class Spider:
    base_url = 'https://www.sephora.cn'
    custom_urls_path = DESKTOP_PATH + '/custom_urls.txt'
    spider_result_path = DESKTOP_PATH + '/spider_result.txt'

    def __init__(self):
        pass

    def start(self):
        self.notepad_txt()
        self.__init_spider_result()

        count = 0
        for url in self.read_urls():
            count += 1
            url_info = f'链接{count}: {url}'
            print(url_info, end=' ')
            self.save_spider_result(url_info + '\n')

            for attr_info in self.spider_product(url):
                self.save_spider_result(attr_info + '\n')

            self.save_spider_result('\n')

            time.sleep(random.randint(6, 12) / 10)

    def notepad_txt(self):
        if not os.path.exists(self.custom_urls_path):
            with open(self.custom_urls_path, 'w', encoding='utf-8') as f:
                f.write('从第二行开始输入url，每个url占一行，输入完后关闭记事本: ')

        os.popen(f'notepad "{self.custom_urls_path}"').read()

    def read_urls(self):
        with open(self.custom_urls_path, 'r', encoding='utf-8') as f:
            count = 0
            for line in f:
                count += 1
                if count == 1:
                    continue
                yield line.strip().replace(' ', '')

    def save_spider_result(self, _info):
        with open(self.spider_result_path, 'a+', encoding='utf-8') as f:
            f.write(_info)

    def __init_spider_result(self):
        with open(self.spider_result_path, 'w', encoding='utf-8') as f:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            f.write(f"爬取时间: {current_time}\n\n")

    @staticmethod
    def check_url(url):
        if url.startswith('https://www.sephora.cn/product/'):
            if url.endswith('.html'):
                pass
            else:
                return '链接必须以.html结尾'

            if '/' in url.lstrip('https://www.sephora.cn/product/'):
                return '链接错误'

        elif url.startswith('http://www.sephora.cn/product/'):
            if url.endswith('.html'):
                pass
            else:
                return '链接必须以.html结尾'

            if '/' in url.lstrip('https://www.sephora.cn/product/'):
                return '链接错误'

        elif url.startswith('https://www.sephora.com') or url.startswith('http://www.sephora.com'):
            return '仅支持中文网站'

        else:
            return '链接错误'

        return True

    def spider_product(self, url):
        check_res = self.check_url(url)
        if check_res is not True:
            product_info = f'{check_res}'
            print(product_info)
            self.save_spider_result(product_info + '\n\n')
            return

        res = self.request_get(url)
        content = res.content
        html = content.decode('utf-8')

        with open('./aa.html', 'w', encoding='utf-8') as f:
            f.write(html)
        mat_obj = re.search('window.__INITIAL_STATE__ = (.*?)window.__INITIAL_ENV__ =', html, re.S)
        if not mat_obj:
            raise Exception('mat_obj')

        res_dict = json.loads(mat_obj.group(1).strip().rstrip(';'))
        # from pprint import pprint#
        # pprint(res_dict)#
        # exit()#
        try:
            p_results = res_dict['productDetailImage']['results']
            if len(p_results) == 1:
                product_id = p_results[0]['productId']
                sku_id = p_results[0]['skuId']
            else:
                raise Exception('p_results error')
        except Exception as e:
            product_info = '链接 Error, 未找到商品'
            print(product_info)
            self.save_spider_result(product_info + '\n\n')
            del e
            return

        print('')

        price = self.request_price(product_id)

        p_info_results = res_dict['productInfo']['results']
        title_cn = p_info_results['productNameCN']  # 商品名称-中文
        title_en = p_info_results['productNameEN']  # 商品名称-英文
        brand_cn = p_info_results['brandInfoDto']['brandNameCN']
        brand_en = p_info_results['brandInfoDto']['brandNameEN']
        # has_inventory = res_dict['productDetail']['PRODUCT_INVENTORY']#
        # has_inventory = "有" if has_inventory else "无"#
        product_info = f'商品: {title_cn} {title_en}  价格: ￥{price}  品牌: {brand_cn} {brand_en}'
        print(product_info)
        self.save_spider_result(product_info + '\n')

        results = self.request_concrete_spec(product_id, sku_id)
        attr_count = 0

        for attr in self.prod_attrs(results):
            attr_count += 1
            attr_info = '(%d). ' % attr_count + '  |  '.join([f'{k}: {v}' for k, v in attr.items() if v is not None])
            print(attr_info)
            yield attr_info

        print('')

    def request_price(self, product_id):
        url = 'https://api.sephora.cn/v2/product/sku/promotion/PC/%d' % product_id
        res_dict = self.request_get(url).json()
        price = res_dict['results']['currentSkuOfferPrice']
        # inventory = res_dict['results']['currentSkuInventory']#
        return price

    def __request_optional_spec(self, product_id, sku_id):
        url = 'https://api.sephora.cn/v1/product/sku/optionalSkuSpec' \
              '?productId=%d' \
              '&skuId=%d' \
              '&channel=PC' \
              '&isPromotion=false' % (product_id, sku_id)
        res = self.request_get(url)
        return res.json()

    def request_concrete_spec(self, product_id, sku_id):
        res_dict = self.__request_optional_spec(product_id, sku_id)

        if not res_dict['results']['colorSeriesNum']:  # 0 or 1~N
            return res_dict['results']

        else:
            url = 'https://api.sephora.cn/v1/product/sku/concreteColor' \
                  '?productId=%d' \
                  '&colorValue=' \
                  '&colorMaterial=' % product_id
            res = self.request_get(url)
            return res.json()['results']

    def prod_attrs(self, results):
        if 'skuSaleAttrs' in results:
            attrs = results['skuSaleAttrs']
            for attr in attrs:
                color = attr['color']  # 颜色值
                color_img_url = attr['colorMaterialImg']  # 颜色图片路径，有的需base_url
                custom = attr['custom']  # 配置名称，色号名称
                inventory = attr['inventory']  # 库存
                spec_img_url = attr['specImageUrl']  # 颜色图片url
                yield {
                    '色号名称': custom, '库存': inventory,
                    '颜色值': color, '颜色图片url': self.modify_img_url(color_img_url),
                    '颜色图片url_1': self.modify_img_url(spec_img_url)
                }

        elif 'prodColorSpecDtoList' in results:
            attrs = results['prodColorSpecDtoList']
            for attr in attrs:
                color_material = attr['colorMaterial']  # 颜色材质
                color_series = attr['colorSeries']  # 颜色系
                color_value = attr['colorValue']  # 颜色值
                color_img_url = attr['colorMaterialImg']  # 颜色图片路径，有的需base_url
                custom = attr['name']  # 配置名称，色号名称
                inventory = attr['inventory']  # 库存
                yield {
                    '色号名称': custom, '库存': inventory,
                    '颜色材质': color_material, '颜色系': color_series,
                    '颜色值': color_value, '颜色图片url': self.modify_img_url(color_img_url),
                }

        else:
            print(results)
            raise Exception('results error')

    def modify_img_url(self, url):
        if not url:
            return
        if url.startswith('https') or url.startswith('https'):
            return url
        else:
            return self.base_url + url

    @staticmethod
    def request_get(url):
        # print('GET', url)#debug
        try:
            res = _requests.get(url, headers={}, timeout=20)
        except Exception as e:
            print(e)
            raise e
        if res.status_code == 200:
            return res
        else:
            print(res.status_code)
            print(res.text)
            print(url)
            raise Exception('request_get status_code')


if __name__ == '__main__':
    spider = Spider()
    # spider.spider_product('https://www.sephora.cn/product/3460.html')
    # spider.spider_product('https://www.sephora.cn/product/985738.html')
    # spider.spider_product('https://www.sephora.cn/product/985738.html')
    while True:
        spider.start()
        print('约5分钟之后继续爬取')
        time.sleep(random.randint(3121, 3652) / 10)
