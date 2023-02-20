import requests
from datetime import datetime
import json
import codecs


class WBParse:

    page_number = 1
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    }

    def check_rating(self, jackets_data_list):
        result = []
        current_time = datetime.now()
        today = datetime(current_time.year, current_time.month, current_time.day)
        for jacket in jackets_data_list:
            url = f"https://feedbacks1.wb.ru/feedbacks/v1/{jacket['feedback_page_id']}"
            req = requests.get(url=url, headers=self.headers)
            feedbacks = req.json()["feedbacks"]
            if feedbacks:
                for feedback in feedbacks:
                    if feedback['productValuation'] in [1, 2]:
                        if feedback['updatedDate']:
                            time_upd = [int(t) for t in feedback['updatedDate'][:10].split("-")]
                            time_upd = datetime(time_upd[0], time_upd[1], time_upd[2])
                            difference = int(str(today - time_upd).split()[0])
                            if difference < 14:
                                result += [(jacket['name'], f"https://www.wildberries.ru/catalog/{jacket['item_id']}/detail.aspx")]
                                #print(f"https://www.wildberries.ru/catalog/{jacket['item_id']}/detail.aspx")
                                break
                        else:
                            time_crt = [int(t) for t in feedback['createdDate'][:10].split("-")]
                            time_crt = datetime(time_crt[0], time_crt[1], time_crt[2])
                            difference = int(str(today - time_crt).split()[0])
                            if difference < 14:
                                result += [(jacket['name'], f"https://www.wildberries.ru/catalog/{jacket['item_id']}/detail.aspx")]
                                #print(f"https://www.wildberries.ru/catalog/{jacket['item_id']}/detail.aspx")
                                break
        return result
            #if feedback['updatedDate']:
            #    print(f"Оценка: {feedback['productValuation']}\nТекст:{feedback['text']}\n"
            #          f"Дата добавления:{feedback['createdDate'][:10]}\nДата обновления:{feedback['updatedDate'][:10]}")
            #else:
            #    print(f"Оценка: {feedback['productValuation']}\nТекст:{feedback['text']}\nДата добавления:{feedback['createdDate'][:10]}")
            #return

    def get_pages(self):
        page_count = 0
        while True:
            url = f"https://catalog.wb.ru/sellers/catalog?appType=1&couponsGeo=2,7,3,6,19,21,8&curr=rub&dest=-2227607&emp=0&lang=ru&locale=ru&page={self.page_number}&pricemarginCoeff=1.0&reg=1&regions=80,64,83,4,38,33,70,68,69,86,30,40,48,1,22,66,31&sort=rate&spp=25&sppFixGeo=4&subject=168&supplier=5359"
            req = requests.get(url=url, headers=self.headers)
            try:
                json_response = req.json()
                if len(json_response['data']['products']) > 0:
                    print(f"Парсинг страницы{self.page_number}")
                    page_count += 1
                    with open(f"pages/jackets_page_{self.page_number}.json", "w", encoding="utf-8") as file:
                        json.dump(json_response['data'], file, indent=4, ensure_ascii=False)
                else:
                    break
            except requests.exceptions.JSONDecodeError:
                print("ошибка")
                break
            finally:
                self.page_number += 1
        print(f"Собраны данные с {page_count} страниц")
        return page_count

    def get_data_from_pages(self, count_pages):
        data = []
        page_counter = 1
        while page_counter <= count_pages:
            with codecs.open(f"pages/jackets_page_{page_counter}.json", "r", "utf-8") as file:
                page_data = json.loads(file.read())['products']
                for product in page_data:
                    str_id = str(product['id'])
                    id_length = len(str_id)
                    variants = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
                    if id_length == 8:
                        for v in variants:
                            url = f"https://basket-{v}.wb.ru/vol{str_id[:3]}/part{str_id[:5]}/{str_id}/info/ru/card.json"
                            req = requests.get(url=url, headers=self.headers)
                            if req.status_code != 404:
                                json_response = req.json()
                                data.append(
                                    {'item_id': json_response['nm_id'], 'feedback_page_id': json_response['imt_id'],
                                     'name': json_response['imt_name']})
                                break
                    else:
                        for v in variants:
                            url = f"https://basket-{v}.wb.ru/vol{str_id[:4]}/part{str_id[:6]}/{str_id}/info/ru/card.json"
                            req = requests.get(url=url, headers=self.headers)
                            if req.status_code != 404:
                                json_response = req.json()
                                data.append(
                                    {'item_id': json_response['nm_id'], 'feedback_page_id': json_response['imt_id'],
                                     'name': json_response['imt_name']})
                                break
            page_counter += 1

        return data

    def main(self):
        cnt = self.get_pages()
        if cnt > 0:
            data = self.get_data_from_pages(cnt)
            result = self.check_rating(data)
            for row in result:
                print(row)
            #with open("pages/needed_data.json", "w", encoding="utf-8") as file:
            #    json.dump(data, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    print(datetime.now())
    wbp = WBParse()
    wbp.main()
    print(datetime.now())

#url для того чтобы узнать id страницы с отзывами https://basket-01.wb.ru/vol71/part7157/7157367/info/ru/card.json, метод гет

#url страницы с отзывами https://feedbacks1.wb.ru/feedbacks/v1/5534016, метод пост

#url самой страницы https://www.wildberries.ru/webapi/brands/data/tvoe/futbolki---topy?sort=rate&page= + номер страницы, метод пост

#url для курток f"https://catalog.wb.ru/sellers/catalog?appType=1&couponsGeo=2,7,3,6,19,21,8&curr=rub&dest=-2227607&emp=0&lang=ru&locale=ru&page={page_number}&pricemarginCoeff=1.0&reg=1&regions=80,64,83,4,38,33,70,68,69,86,30,40,48,1,22,66,31&sort=rate&spp=25&sppFixGeo=4&subject=168&supplier=5359"

#одна куртка https://basket-09.wb.ru/vol1260/part126000/126000336/info/ru/card.json, нужны imt_id и nm_id

#отзывы для курток https://feedbacks2.wb.ru/feedbacks/v1/ + номер, который отличается от id (imt_id)