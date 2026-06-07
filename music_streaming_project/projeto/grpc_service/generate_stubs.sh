#!/bin/bash
# Execute este script dentro da pasta grpc_service/ para gerar os stubs Python
echo "Gerando stubs gRPC a partir de music.proto..."
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. music.proto
echo "Stubs gerados: music_pb2.py e music_pb2_grpc.py"
