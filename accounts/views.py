from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status , filters
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from django.contrib.auth import login,logout
from rest_framework_simplejwt.views import TokenObtainPairView
# from rest_framework.generics import CreateAPIView
# from .models import CustomUser

# Create your views here.

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserViewset(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes =[IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name','phone_number']

    def get_serializer_class(self):
        if self.action in ['list','retrieve']:
            return UserProfileSerializer
        return UserSerializer
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    @action(detail=False ,methods= ['get'])
    def me(self,request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    @action(detail=False , methods=['put','patch'])
    def update_profile(self,request):
        serializer =  UserProfileSerializer(request.user,data = request.data,partial = True)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
    @action(detail=False,methods=['post'])
    def change_password(self,request):
        serializer = PasswordChangeSerializer(data =request.data , context = {'request':request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'message': 'Password updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AuthViewsets(viewsets.ViewSet):
    @action(detail=False,methods=['post'])
    def register(self,request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            token,created = Token.objects.get_or_create(user=user) #created here is boolen that tells weather token has been generated for it before or not
            return Response({
                'user':UserProfileSerializer(user).data,
                'token':token.key
            })
        return Response(serializer.errors ,status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,methods=['post'])
    def logout(self,request):
        try:
            request.user.auth_token.delete()
        except:
            pass
        logout(request)
        return Response({"message":"User is logged out Successfully"},status=status.HTTP_200_OK)    
        








# class RegisterView(APIView):
#     def post(self,request):
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             user=serializer.save()

            
#             refresh = RefreshToken.for_user(user)

#             return Response({'user':serializer.data,'refresh':str(refresh),'acess':str(refresh.access_token)},status=status.HTTP_201_CREATED)
#         return Response(serializer.errors,status=status.HTTP_401_UNAUTHORIZED)
    


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

