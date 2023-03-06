import websockets
import asyncio
import json


async def main():
    futures_name = 'XRPUSDT'.lower()
    url1 = f"wss://stream.binance.com:9443/stream?streams={futures_name}@kline_1h"
    url2 = f"wss://stream.binance.com:9443/stream?streams={futures_name}@trade"
    async with websockets.connect(url2) as client:
        while True:
            data2 = json.loads(await client.recv())['data']
            actual_time = data2['t']
            actual_cost = float(data2['p'])
            async with websockets.connect(url1) as client1:
                max_cost = float(json.loads(await client1.recv())['data']['k']['h'])
            cost_difference = (max_cost - actual_cost) / actual_cost * 100
            if cost_difference >= 1:
                print(f"Цена упала на 1%.\nМаксимальная цена за последний час: {max_cost}\nТекущая цена: {actual_cost}")
            print(f"Время: {actual_time}, текущая стоимость: {actual_cost}, максимальная стоимость за час: {max_cost}\n"
                  f"Разность стоимости в процентах: {cost_difference}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
