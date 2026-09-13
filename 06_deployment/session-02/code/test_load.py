import asyncio
import time
import httpx


async def make_request(client,url,request_id):
    start = time.time()
    print(f"Request {request_id}: {start}")
    response = await client.get(url)
    end = time.time()
    print(f"Request {request_id}: {end - start}")



async def main():
    # testing for flask api
    start_flask = time.time()
    async with httpx.AsyncClient() as client:
        tasks = [
            make_request(client, "http://localhost:5000/order", i) for i in range(1, 6)

        ]
        await asyncio.gather(*tasks)
    end_flask = time.time()
    print(f"Flask server response time: {end_flask - start_flask}")
    # fast api
    start_fastapi = time.time()
    async with httpx.AsyncClient() as client:
        tasks = [
            make_request(client, "http://localhost:8000/order", 1),
            make_request(client, "http://localhost:8000/order", 2),
            make_request(client, "http://localhost:8000/order", 3),
            make_request(client, "http://localhost:8000/order", 4),
            make_request(client, "http://localhost:8000/order", 5)

        ]
        await asyncio.gather(*tasks)
    end_fastapi = time.time()
    print(f"FastAPI server response time: {end_fastapi - start_fastapi}")


if __name__ == "__main__":
    asyncio.run(main())