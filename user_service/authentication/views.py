from rest_framework.response import Response
from rest_framework.decorators import api_view



@api_view(['GET'])
def test_endpoint(request):
    return Response(
        {
            "Message": "Successfully Hitted."
        },
        status=200
    )