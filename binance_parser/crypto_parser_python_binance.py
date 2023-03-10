from binance import AsyncClient
import asyncio


async def main():
    client = await AsyncClient.create()
    needed = -1
    req1 = await client.get_products()
    all_symbs = req1['data']
    for i in range(len(all_symbs)):
        if all_symbs[i]['s'] == 'XRPUSDT':
            needed = i
            break
    if needed != -1:
        while True:
            req1 = await client.get_products()
            actual_cost = float(req1['data'][needed]['c'])  # Для получения текущей стоимости фьючерса
            req2 = await client.get_historical_klines(symbol='XRPUSDT', interval='1h', limit=1)
            max_cost = float(req2[0][2])  # Для получения максимума за час
            cost_difference = (max_cost - actual_cost) / actual_cost * 100
            if cost_difference >= 1:
                print(f"Цена упала на 1%.\nМаксимальная цена за последний час: {max_cost}\nТекущая цена: {actual_cost}")
            print(f"Текущая стоимость: {actual_cost}, максимальная стоимость: {max_cost}, Разница: {cost_difference}%")
    await client.close_connection()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
