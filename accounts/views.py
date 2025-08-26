from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken

# from rest_framework.generics import CreateAPIView
# from .models import CustomUser



# Create your views here.

class RegisterView(APIView):
    def post(self,request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.save()

            
            refresh = RefreshToken.for_user(user)

            return Response({'user':serializer.data,'refresh':str(refresh),'acess':str(refresh.access_token)},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_401_UNAUTHORIZED)
    

# class RegisterGenericview(CreateAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = RegisterSerializer

#     def create(self, request,*args,**kwargs):
#         response = super.create(request,*args,**kwargs)
#         user = self.get_queryset.get(email = response.data['email'])

#         refresh = RefreshToken.for_user(user)

#         response.data['refresh'] =str(refresh)
#         response.data['access'] =str(refresh.access_token)

#         return response

