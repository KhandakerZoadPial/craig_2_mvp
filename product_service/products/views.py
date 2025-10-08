from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from .utils import generate_response
from .permissions import IsJWTAuthenticated


@api_view(['GET', 'POST'])
@permission_classes([IsJWTAuthenticated])
def product_list_create_view(request):
    print('here')
    user_id = int(request.token_payload.get('user_id'))
    print(request.token_payload)

    if request.method == 'GET':
        products = Product.objects.filter(owner_id=user_id)
        serializer = ProductSerializer(products, many=True)
        response_data = generate_response(status="success", code=200, data=serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner_id=user_id)
            response_data = generate_response(status="success", code=201, data=serializer.data)
            return Response(response_data, status=status.HTTP_201_CREATED)
        response_data = generate_response(status="failure", code=400, error=serializer.errors)
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)





@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsJWTAuthenticated])
def product_detail_view(request, pk):
    user_id = int(request.token_payload.get('user_id'))

    try:
        product = Product.objects.get(pk=pk, owner_id=user_id)
    except Product.DoesNotExist:
        response_data = generate_response(status="failure", code=404, error="Product not found.")
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        response_data = generate_response(status="success", code=200, data=serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    elif request.method == 'PATCH':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_data = generate_response(status="success", code=200, data=serializer.data)
            return Response(response_data, status=status.HTTP_200_OK)
        response_data = generate_response(status="failure", code=400, error=serializer.errors)
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        product.delete()
        response_data = generate_response(status="success", code=204, data={"message": "Product deleted successfully."})
        return Response(response_data, status=200)