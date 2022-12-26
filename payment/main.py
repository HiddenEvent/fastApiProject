from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host="redis-16976.c80.us-east-1-2.ec2.cloud.redislabs.com",
    port="16976",
    password="nw5IYXuZ0xRJ6dzUxGmMaCVBCxyxomo5",
    decode_responses=True
)


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str # pending, completed, refunded

    class Meta:
        database = redis


@app.post('/orders')
async def create(request: Request):
    body = await request.json()
    response = requests.get('http://localhost:8000/products/%s' % body['id'])
    product = response.json()

    order = Order(product_id=body['id'], price=product['price'], fee=0.2 * product['price'],
                  total=1.2 * product['price'], quantity=body['quantity'], status='pending')
    order.save()

    order_completed(order)
    return order

def order_completed(order: Order):
    order.status = 'completed'
    order.save()


