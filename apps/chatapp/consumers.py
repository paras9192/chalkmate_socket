import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.files.base import ContentFile
import base64
from apps.accounts.models import User
import requests
from django.conf import settings

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print('hi')
        query_params = self.scope["query_string"].decode("utf-8").split("&")
        params_dict = dict(param.split("=", 1) for param in query_params if "=" in param)
        api_key = params_dict.get("api_key")
        api_password = params_dict.get("api_password")
        user_id = params_dict.get("user_id")
        
        # if not self.authenticate(api_key, api_password):
        #     self.close(code=4001)  
        #     return
        # response=self.call_channel_subscription_api(user_id)
        # print(response)
        personal_group_name = f"user_notifications_{user_id}"
        async_to_sync(self.channel_layer.group_add)(
            personal_group_name,
            self.channel_name
        )
        # async_to_sync(self.channel_layer.group_send)(
        #     personal_group_name,
        #     {
        #         'type': 'send_dm_list',
        #         'message': {
        #             "event":"send_dm_list",
        #             "data": response['data'] 
        #         }  
        #     }
        # )
        print('hi i am connected ')
        self.accept()
    def disconnect(self, code):
        if hasattr(self, 'room_group_name'):
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )

    def authenticate(self, api_key, api_password):
        """
        Your authentication logic goes here.
        You can query the database to verify the API key and password.
        """
        try:
            user = User.objects.get(api_key=api_key, secret=api_password)
            return True if user else False
        except User.DoesNotExist:
            return False

    def receive(self, text_data):
        data_json = json.loads(text_data)
        if data_json.get("event") == "update_message":

            # Handle message update
            self.handle_message_update(data_json)
        else:
            # Handle new message or file
            if "file_base64" in data_json:
                file_str = data_json["file_base64"]
                file_format = data_json["format"]
                file_name = f'file_{self.channel_id}.{file_format.split("/")[-1]}'
                file = ContentFile(base64.b64decode(file_str), name=file_name)
                # Process file if needed

            self.handle_new_message(data_json)
    def handle_message_update(self, data_json):
    
        message_data = data_json.get("message", {})
        message_id = message_data.get("msg_id") 
        updated_message = message_data.get("content")  
        channel_id = data_json.get("channel_id")
        if not message_id or not updated_message:
            return

        response = self.call_get_subscription_api(channel_id)
        for recipient in response['data']:
            recipient_id_str = str(recipient['recipient'])
        
            personal_group_name = f"user_notifications_{recipient_id_str}"
            async_to_sync(self.channel_layer.group_send)(
            personal_group_name,
            {
                "type": "update_message",
                "message": "messsage updated successfully",
                "channel_id": data_json['channel_id'],
                "message_data": updated_message,
            })
            response=self.call_channel_subscription_api(recipient_id_str)
            personal_group_name = f"user_notifications_{recipient_id_str}"
            async_to_sync(self.channel_layer.group_add)(
            personal_group_name,
            self.channel_name
        )
            async_to_sync(self.channel_layer.group_send)(
            personal_group_name,
            {
                'type': 'send_dm_list',
                'message': {
                    "event":"send_dm_list",
                    "data": response['data'] 
                }  
            }
        )
    

    def handle_new_message(self, data_json):
        print("hi new message")
        async_to_sync(self.channel_layer.group_send)(
        f"channel_chat_{data_json['channel_id']}",
        {
            "type": "chat_message",
            "message_data": data_json,
        }
    )
        response = self.call_get_subscription_api(data_json['channel_id'])
        print(response)
        for recipient in response['data']:
            recipient_id_str = str(recipient['recipient'])
        
            personal_group_name = f"user_notifications_{recipient_id_str}"
            async_to_sync(self.channel_layer.group_send)(
            personal_group_name,
            {
                "type": "new_message_received",
                "message": "sent you a message",
                "channel_id": data_json['channel_id'],
                "message_data": data_json,
            })
            response=self.call_channel_subscription_api(recipient_id_str)
            personal_group_name = f"user_notifications_{recipient_id_str}"
            async_to_sync(self.channel_layer.group_add)(
            personal_group_name,
            self.channel_name
        )
            async_to_sync(self.channel_layer.group_send)(
            personal_group_name,
            {
                'type': 'send_dm_list',
                'message': {
                    "event":"send_dm_list",
                    "data": response['data'] 
                }  
            }
        )
    

    def update_message(self, event):
        """
        This method handles the updated message event.
        It sends the updated message data to the WebSocket client.
        """
        self.send(
            text_data=json.dumps({
                "message": event["message"],
                "channel_id": event["channel_id"],
                "message_data": event["message_data"]
            })
        )
    def send_dm_list(self, event):
        message = event['message']
        
        if isinstance(message, (list, dict)):
            message = json.dumps(message) 
        self.send(text_data=message)
        
    def new_message_received(self, event):
        """
        Handle 'new_message_received' type messages.
        Send the notification to the WebSocket client.
        """
        self.send(
            text_data=json.dumps({
                "message": event["message"],
                "channel_id": event["channel_id"],
                "message_data": event["message_data"]
            })
        )
    
        
    # def subscribe_to_user_channels(self):
    #     """
    #     Subscribe the user to all channels they are a part of.
    #     This method assumes that a user can be subscribed to multiple channels like DMs or group chats.
    #     """
    #     # Get all channels that the user is subscribed to

    #     for subscription in user_channels:
    #         room_group_name = f"channel_chat_{subscription.channel.id}"

    #         # Subscribe the user to each channel (group)
    #         async_to_sync(self.channel_layer.group_add)(
    #             room_group_name,
    #             self.channel_name
    #         )
        
        
        
        
        
        
        
        
    def call_channel_subscription_api(self, user_id):
        # Define the base URL for your API
        
        base_url = settings.BACKEND_SERVER_URL
        endpoint = f"{base_url}/api/v1/chat/channel-subscriptions/?user_id={user_id}"
        # Make the API call
        try:
            response = requests.get(endpoint)

            if response.status_code == 200:
                json_response = response.json()
                return json_response
            else:
                print(f"Failed to subscribe: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error while calling channel subscription API: {e}")
    def call_get_subscription_api(self, channel_id):
        base_url = settings.BACKEND_SERVER_URL
        endpoint = f"{base_url}/api/v1/chat/channel-subscriptions/by_channel?channel_id={channel_id}"
        try:
            response = requests.get(endpoint, json={})

            if response.status_code == 200:
                json_response = response.json()
                return json_response
            else:
                print(f"Failed to subscribe: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error while calling channel subscription API: {e}")
        
        
        
        

        
        
        
