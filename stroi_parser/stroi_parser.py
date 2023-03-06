import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
import json
import aiohttp


class StroiParse:

    base_url_site1 = "https://psk-holding.ru/catalog/"
    base_url_site2 = "https://pmg.su"
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    }

    async def get_first_site_categories(self, session):
        page_1 = await session.get(url=self.base_url_site1, headers=self.headers)
        with open("site1_main_page.html", "w", encoding="utf-8") as file:
            file.write(await page_1.text())
        with open("site1_main_page.html", encoding='utf-8') as file:
            src = file.read()
        soup = BeautifulSoup(src, "lxml")

        cats_list = soup.find('div', class_='cats').find_all('div', class_='link')
        sub_cats_list = soup.find('div', class_='cats').find_all('div', class_='sub_cats')
        cats_and_subcats = {}
        domanin = "https://psk-holding.ru/"
        for i in range(len(cats_list)):
            cat_name = cats_list[i].text.replace('\n', '')
            cats_and_subcats[cat_name] = sub_cats_list[i].find_all('a')
            cats_and_subcats[cat_name] = [domanin + tag.get('href') for tag in cats_and_subcats[cat_name]]
        with open("json_results/tmp_site1.json", "w", encoding="utf-8") as file:
            json.dump(cats_and_subcats, file, indent=4, ensure_ascii=False)
        return cats_and_subcats

    async def get_second_site_categories(self, session):
        page_2 = await session.get(url=self.base_url_site2, headers=self.headers)
        with open("site2_main_page.html", "w", encoding="utf-8") as file:
            file.write(await page_2.text())
        with open("site2_main_page.html", encoding='utf-8') as file:
            src = file.read()
        soup = BeautifulSoup(src, "lxml")
        cats_list = soup.find_all('div', class_="our-services__item h-100")
        cats_and_subcats = {}
        domain = self.base_url_site2
        for cat in cats_list:
            name_of_cat = cat.find('div', class_='our-services__title mb-3').text
            cats_and_subcats[name_of_cat] = cat.find_all('li')
            for i in range(len(cats_and_subcats[name_of_cat])):
                if domain in cats_and_subcats[name_of_cat][i].find('a').get('href'):
                    cats_and_subcats[name_of_cat][i] = cats_and_subcats[name_of_cat][i].find('a').get('href')
                else:
                    cats_and_subcats[name_of_cat][i] = domain + cats_and_subcats[name_of_cat][i].find('a').get('href')
        with open("json_results/tmp_site2.json", "w", encoding="utf-8") as file:
            json.dump(cats_and_subcats, file, indent=4, ensure_ascii=False)
        return cats_and_subcats

    def category_overrun(self, categories_dict: dict, session):
        pass

    async def get_one_category_goods_site1(self, categories_dict: dict, session):
        result = []
        lst = list(categories_dict.keys())
        for cat in lst:
            subcats_list = categories_dict[cat]
            for subcat in subcats_list:
                req = await session.get(url=subcat, headers=self.headers)
                filename = f"all_pages/{subcat.split('/')[2]}-{subcat.split('/')[5]}.html"
                #with open(filename, "w", encoding="utf-8") as file:
                #    file.write(req.text)
                #with open(filename, encoding="utf-8") as file:
                #    src = file.read()
                src = await req.text()
                soup = BeautifulSoup(src, "lxml")
                title = soup.find('h1').text
                fl = True
                #table = soup.find('section', class_='products block ctlg section-catalog').find_all('a')
                try:
                    table = soup.find('section', class_='products block ctlg section-catalog').find_all('a', class_="product")
                    for el in table:
                        try:
                            name = el.find('div', class_='name').text.strip()
                            price = el.find('div', class_='price_info').text.strip()
                        except AttributeError:
                            name = price = "-"
                            fl = False
                        finally:
                            result.append(
                                {'name': name, 'cat_name': cat, 'url': subcat, 'price': price})
                except AttributeError:
                    fl = False
                    result.append(
                        {title: 'Нет данных'})

                if fl:
                    print(f'{title} - собраны все данные')
                else:
                    print(f'{title} - собраны не все данные')
        with open("json_results/detail_tmp_site1.json", "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    async def get_one_category_goods_site2(self, categories_dict: dict, session):
        result = []
        lst = list(categories_dict.keys())
        for cat in lst:
            subcats_list = categories_dict[cat]
            for subcat in subcats_list:
                req = await session.get(url=subcat, headers=self.headers)
                filename = f"all_pages/{subcat.split('/')[2]}-{subcat.split('/')[3]}.html"
                with open(filename, "w", encoding="utf-8") as file:
                    file.write(await req.text())
                with open(filename, encoding="utf-8") as file:
                    src = file.read()
                soup = BeautifulSoup(src, "lxml")
                title = soup.find('h1').text
                fl = True
                if lst.index(cat) == 0:
                    price_list = []
                    try:
                        table = soup.find('div', class_='tab-content mb-5').find('div', class_='d-none d-md-block')
                        hdrs = [el.text for el in table.find('div', class_='row table-thead').find_all('div')]
                        values = [el.find_all('div') for el in table.find_all('div', class_='row')[1:]]
                        for i in range(len(values)):
                            values[i] = [div.text for div in values[i]]
                        for val in values:
                            tmp = {}
                            for i in range(len(hdrs)):
                                tmp[hdrs[i]] = val[i]
                            price_list.append(tmp)
                        result.append({'name': title, 'cat_name': cat, 'url': subcat, 'price_list': price_list})
                    except AttributeError:
                        fl = False
                        result.append({'name': title, 'cat_name': cat, 'url': subcat,
                                       'price_list': 'Отсутствует/нужно запросить'})

                elif lst.index(cat) == 1:
                    fl = False
                    result.append(
                        {'name': title, 'cat_name': cat, 'url': subcat, 'price_list': 'Отсутствует/нужно запросить'})
                elif lst.index(cat) == 2:
                    price_list = []
                    try:
                        table = soup.find('div', class_='tab-content mb-5').find('div',
                                                                                 class_='tab-pane fade show active')
                        hdrs = table.find('div', class_='col-12 col-md-7 col-xl-6').find('div',
                                                                                         class_='row table-thead')
                        hdrs = [el.text for el in hdrs.find_all('div')]
                        values = [el.find_all('div') for el in
                                  table.find('div', class_='col-12 col-md-7 col-xl-6').find_all('div', class_='row')][
                                 1:]
                        for i in range(len(values)):
                            values[i] = [div.text for div in values[i]]
                        for val in values:
                            tmp = {}
                            for i in range(len(hdrs)):
                                tmp[hdrs[i]] = val[i]
                            price_list.append(tmp)
                        result.append({'name': title, 'cat_name': cat, 'url': subcat, 'price_list': price_list})
                        hdrs = table.find('div', class_='col-12 col-md-5 col-xl-4').find('div',
                                                                                         class_='row table-thead')
                        hdrs = [el.text for el in hdrs.find_all('div')]
                        values = [el.find_all('div') for el in
                                  table.find('div', class_='col-12 col-md-5 col-xl-4').find_all('div', class_='row')][
                                 1:]
                        for i in range(len(values)):
                            values[i] = [div.text for div in values[i]]
                        for val in values:
                            tmp = {}
                            for i in range(len(hdrs)):
                                tmp[hdrs[i]] = val[i]
                            price_list.append(tmp)
                        result.append({'name': title, 'cat_name': cat, 'url': subcat, 'price_list': price_list})
                    except AttributeError:
                        fl = False
                        result.append({'name': title, 'cat_name': cat, 'url': subcat,
                                       'price_list': 'Отсутствует/нужно запросить'})

                elif lst.index(cat) == 3:
                    price_list = []
                    try:
                        table = soup.find_all('div', class_='d-none d-md-block')[0]
                        hdrs = [el.text for el in table.find('div', class_='row table-thead').find_all('div')]
                        values = [el.find_all('div') for el in table.find_all('div', class_='row')[1:]]
                        for i in range(len(values)):
                            values[i] = [div.text for div in values[i]]
                        for val in values:
                            tmp = {}
                            for i in range(len(hdrs)):
                                tmp[hdrs[i]] = val[i]
                            try:
                                tmp.pop("Площадь фасада")
                            except KeyError:
                                pass
                            price_list.append(tmp)
                        result.append({'name': title, 'cat_name': cat, 'url': subcat, 'price_list': price_list})
                    except AttributeError:
                        fl = False
                        result.append({'name': title, 'cat_name': cat, 'url': subcat,
                                       'price_list': 'Отсутствует/нужно запросить'})

                if fl:
                    print(f'{title} - собраны все данные')
                else:
                    print(f'{title} - собраны не все данные')
                # break
        # print(result)
        with open("json_results/detail_tmp_site2.json", "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    async def main(self):
        print(datetime.now())
        async with aiohttp.ClientSession() as session1:
            first_site_cats_and_subcats = await self.get_first_site_categories(session1)
            await self.get_one_category_goods_site1(categories_dict=first_site_cats_and_subcats, session=session1)
        async with aiohttp.ClientSession() as session2:
            second_site_cats_and_subcats = await self.get_second_site_categories(session2)
            await self.get_one_category_goods_site2(categories_dict=second_site_cats_and_subcats, session=session2)
        print(datetime.now())
        #Старт стоп до асинх  19:34:49.471071   19:39:28.221214
        #Старт стоп после асинх


if __name__ == '__main__':
    sp = StroiParse()
    asyncio.get_event_loop().run_until_complete(sp.main())
