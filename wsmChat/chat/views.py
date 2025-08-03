from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets , permissions ,status , filters
from .serlializers import ChatSerializer ,MessageSerializer ,GroupSerilaizer , MessageCreateSerializer ,UserChatSerializer ,UserGroupSerializer
from .models import Chat,Messages,UserChat,UserGroup ,Group
from accounts.models import CustomUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q


class chatViewset(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes  = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields =['name']

    def get_queryset(self):
        return   Chat.objects.filter(users=self.request.user).prefetch_related(
            'users',
            'messages'
        )

    @action(detail=True,methods=['post'])
    def add_user(self,request,pk=None):
        chat = self.get_object()
        user_id = request.data.get('user_id')
        try:
            user =  CustomUser.objects.get(id=user_id)
            user_chat , created = UserChat.objects.get_or_create(user =user ,chat=chat)
            if created:
                return Response({"message":"User Added to chat Successfully"})
            else:
                return Response({"message":"User is already in chat"},status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error":"User Not Found"},status=status.HTTP_404_NOT_FOUND)    
    @action(detail=True,methods=['post'])
    def remove_user(self,request,pk=None):
        chat =  self.get_object()
        user = request.data.get('user_id')

        user_id = request.data.get('user_id')
        try:
            user= CustomUser.objects.get(id=user_id)
            user_chat =UserChat.objects.get(user=user,chat=chat)
            user_chat.delete()
            return Response({"message":"User has been removed from chat"})
        except(UserChat.DoesNotExist or CustomUser.DoesNotExist):
            return Response({"error":"User not found in  chat"},status= status.HTTP_404_NOT_FOUND)    
    @action(detail=True , methods=['get'])
    def get_messages(self,request,pk=None):
        chat = self.get_object()
        messages = chat.messages.select_related('user').order_by('-sent_at')
        page =self.paginate_queryset(messages)

        if page is not None:
            serializer = MessageSerializer(page,many =True)
            return self.get_paginated_response(serializer.data)
        serializer = MessageSerializer(messages)
        return Response(serializer.data)
    @action(detail=True,methods=['get'])
    def get_unread_messages(self,request,pk=None):
        chat = self.get_object()
        unread_messages = chat.messages.select_related('user').filter(seen_at__isnull =True).exclude(user =request.user)
        unread_count = unread_messages.count()
        serializer = MessageSerializer(unread_messages,many=True)
        return Response({
            'unread_count': unread_count,
            'unread_messages':serializer.data
        })

    


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerilaizer
    permission_classes  = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields =['name']

    def  get_queryset(self):
        return Group.objects.filter(users = self.request.user).prefetch_related(
            'users',
            'messages'
        )
    @action(detail=True ,methods=['post'])
    def add_member(self,request,pk):
        group = self.get_objects()
        user_id = request.data.get('user_id')
        is_admin =request.data.get('is_admin',False)
        try:
            user = CustomUser.objects.get(id=user_id)
            user_group,created = UserGroup.objects.get_or_create(user=user,group=group,defaults={'is_admin':is_admin})
            if created:
                return Response({"message":"User has been added"},status=status.HTTP_200_OK)
            else:
                return Response({"message":"User is already in the group"},status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error":"Group Not Found"},status=status.HTTP_404_NOT_FOUND)    
    @action(detail=False,methods=['post'])
    def remove_member(self,request,pk=None):
        group =self.get_object()
        user_id = request.data.get('user_id')
        try:
            user_to_remoove = CustomUser.objects.get(id=user_id)
            current_user = request.user

            user_group = UserGroup.objects.get(user = user_to_remoove , group =group)

            is_admin = UserGroup.objects.filter(user =current_user,group=group ,is_admin=True).exists()
            if is_admin or current_user == user_to_remoove:
                user_group.delete()
                return Response({"message":"Member has been remooved"})
            else:
                return Response({"message":"You Are Not authenticated to remoove the member"},status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            return Response({"error":"User Not Found"},status=status.HTTP_404_NOT_FOUND)
        except UserGroup.DoesNotExist:
            return Response({"error":"USer Not found in Group"},status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True,methods=['post'])
    def make_admin(self,request,pk=None):
        group =self.get_object()
        user_id = request.data.get('user_id')
        try:
            user=CustomUser.objects.get(id=user_id)
            user_group= UserGroup.objects.get(user =user,group=group)
            user_group.is_admin = True
            user_group.save()   
            return Response({"message":"User is Now Admin"})
        except (CustomUser.DoesNotExist , UserGroup.DoesNotExist):
            return Response({"error":"User Not Found in The group"},status=status.HTTP_404_NOT_FOUND)
            
    @action(detail=True,methods=['get'])
    def get_messages(self,request,pk=None):
        group = self.get_object()
        messages = group.Messages.select_relates('user').order_by('-sent_at')

        page = self.paginate_queryset(messages)

        if page is not None:
            serlializer =MessageSerializer(page,many=True)
            return self.get_paginated_response(serlializer.data)
        else:
            serlializer =MessageSerializer(messages , many=True)
            return Response(serlializer.data)
    @action(detail=True,methods=['get'])
    def get_unread_messages(self,request,pk=None):
        group = self.get_object()
        unread_messages = group.messages.select_related('user').filter(seen_at__isnull =True).exclude(user =request.user)
        unread_count = unread_messages.count()
        serializer = MessageSerializer(unread_messages,many=True)
        return Response({
            'unread_count': unread_count,
            'unread_messages':serializer.data
        })


class MessageViewset(viewsets.ModelViewSet):
    serializer_class = MessageSerializer()
    permission_classes =[IsAuthenticated]
    filter_backends = [DjangoFilterBackend , filters.SearchFilter]
    filter_fields = ['chat','group','type']
    search_fiedlds = ['content']

    def get_queryset(self):
        user_chat =Chat.objects.filter(user =self.request.user).values_list('id',flat=True)
        user_group = Group.objects.filter(user =self.request.user).values_list('id',flat=True)

        return Messages.objects.filter(
            Q(chat__in=user_chat) | Q(group__in =user_group)
        ).select_related('user','chat','group').order_by('-sent_at')
    def get_serializer_class(self):
        if self.action =='create':
            return MessageCreateSerializer
        return MessageSerializer
    @action(detail=True , methods=['post'])
    def mark_delivered(self,request,pk=None):
        message = self.get_object()
        if  not message.delivered_at:
            message.delivered_at = timezone.now()
            message.save()
            return Response({"message":"Message is marked as delivered"})

    def mark_seen(self,request,pk=None):
        message =self.get_object()
        if not message.seen_at():
            message.seen_at = timezone.now()
            message.save()
            return Response({"message":"Message is marked as seen"})
    @action(detail=False , methods=['get'])
    def mark_unread(self,request,pk=None):
        user_group  = Group.objects.filter(user = request.user).values_list('id',flat=True)
        user_chat  = Chat.objects.filter(user = request.user).values_list('id',flat=True)

        unread_messages = Messages.objects.filter(
            Q(chat__in = user_chat) | Q(chat__in = user_group)
        ).filter(seen_at__isnull = True).exclude(request.user).select_related('user','chat','group')

        serlializer =  MessageSerializer(unread_messages)
        return Response(serlializer.data)
    

class UserChatViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserChatSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return UserChat.objects.fiilter(user = self.request.user).select_related('user','chat')



class UserGroupViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserGroupSerializer
    permission_classes = [IsAuthenticated]
    def  get_queryset(self):
        return UserGroup.objects.filter(user = self.request.user).select_related('user','group')
    


"""

Bilkul bhai, chalo select_related() ko ekdum simple aur desi example ke through samajhte hain. Yeh concept thoda important hai Django optimization ke liye, toh dhyan se sun:

🔍 Pehle samajho: Normal Query kaise kaam karti hai?

user_chats = UserChat.objects.filter(user=request.user)
for uc in user_chats:
    print(uc.chat.name)
    print(uc.user.name)



❗ Problem:
Yahan agar user_chats mein 10 rows hain, toh:

Pehle query karega UserChat table se → 1 query

Har loop ke andar jab .chat ya .user access karega, toh alag se query karega Chat aur User table se.

🧨 Total: 1 (UserChat) + 10 (Chat) + 10 (User) = 21 queries! 😱
Ye hota hai "N+1 query problem".

✅ Solution: select_related()
user_chats = UserChat.objects.filter(user=request.user).select_related('chat', 'user')
💡 Iska matlab:
"Bhai, mujhe UserChat do, aur uske saath hi Chat aur User ki info bhi ek hi query mein la do."

Ab jab tu loop karega:

for uc in user_chats:
    print(uc.chat.name)  # Already loaded
    print(uc.user.name)  # Already loaded




✅ Kitni queries?
Only 1 query! Django internally SQL JOIN karega:



SELECT * FROM user_chat
LEFT JOIN chat ON user_chat.chat_id = chat.id
LEFT JOIN user ON user_chat.user_id = user.id
WHERE user_chat.user_id = X;



🔄 Recap: Jab select_related() use karna hai?
Situation	Use select_related()?
ForeignKey / OneToOne hai	✅ Yes, best use-case
ManyToMany hai	❌ No, use prefetch_related()
💬 Tere example mein:
UserChat.objects.filter(user=self.request.user).select_related('user', 'chat')
Yeh keh raha hai:

Mujhe UserChat records de de jo current user ke hain

Aur saath hi us chat aur user object ko bhi fetch kar ke la de

Takki loop mein access karte waqt baar-baar database hit na ho




"""








# class Get_User_Serializer(generics.ListAPIView):
#     serializer_class = GetUsers
#     permission_classes = [AllowAny]

#     def get_queryset(self):
#         return CustomUser.objects.all()



# class ChatListCreateView(generics.ListCreateAPIView):
#     serializer_class = ChatSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Chat.objects.filter(participants = self.request.user)
    
#     def perform_create(self, serializer):
#         serializer.save()
#         # Chat.participants.add(self.request.user)


# class MessagesListCreateView(generics.ListCreateAPIView):
#     serializer_class = MessageSerializer
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser,FormParser]

#     def perform_create(self, serializer):
#       serializer.save(sender = self.request.user)

#     def get_queryset(self):
#         chat_id = self.kwargs['chat_id']
#         user = self.request.user

#         try:
#             chat_instance = Chat.objects.get(id = chat_id)
#         except Chat.DoesNotExist:
#             raise PermissionDenied("Chat Does not exist") 
        
#         if user not in chat_instance.participants.all():
#             raise PermissionDenied("User is not the part of Chat")
        
#         return Messages.objects.filter(Chat = chat_instance).order_by('timestamp')

