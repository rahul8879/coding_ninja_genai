# lets build the image

docker build -t policy-scaling-demo:1.0 .

# run one container
docker run -d \
  --name scaling-app-1 \
  -p 8001:8000 \
  -e INSTANCE_NAME=app-1 \
  policy-scaling-demo:1.0


# now lets hit the api ---> 
curl -s http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"How many annual leaves do I get?"}' \
  | python3 -m json.tool



# so lets create more instance --->
3 isntance 

docker run -d \
  --name scaling-app-2 \
  -p 8002:8000 \
  -e INSTANCE_NAME=app-2 \
  policy-scaling-demo:1.0

docker run -d \
  --name scaling-app-3 \
  -p 8003:8000 \
  -e INSTANCE_NAME=app-3 \
  policy-scaling-demo:1.0


# use Nginx for load balance

# lets connect all the container/instance on same docker network
docker network create scaling-net
docker network connect scaling-net scaling-app-1
docker network connect scaling-net scaling-app-2
docker network connect scaling-net scaling-app-3


# Lets define the nginix conf file --> giving info about instance


docker run -d \
  --name scaling-nginx \
  --network scaling-net \
  -p 8080:80 \
  -v "$(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro" \
  nginx:stable-alpine