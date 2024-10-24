import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.files.base import ContentFile
import base64
from apps.accounts.models import User
import requests
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer
class ChatConsumer(WebsocketConsumer):

    def connect(self):
        query_params = self.scope["query_string"].decode("utf-8").split("&")
        params_dict = dict(param.split("=", 1) for param in query_params if "=" in param)
        api_key = params_dict.get("api_key")
        api_password = params_dict.get("api_password")
        user_id = params_dict.get("user_id")
        recipient_id_str = str(user_id)
        
        if not self.authenticate(api_key, api_password):
            self.close(code=4001)  
            return
        response=self.call_channel_subscription_api(user_id)
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
        print(data_json)
        if data_json.get("event") == "update_message":
            self.handle_message_update(data_json)
        elif data_json.get("event") == "delete_channel":
            self.delete_channel_handle(data_json)
        # if data_json.get("event") == "error_message":
        #     self.handle_send_error_message(data_json)
        elif data_json.get("event") == "chat_message":
            # Handle new message or file
            if "file_base64" in data_json:
                file_str = data_json["file_base64"]
                file_format = data_json["format"]
                file_name = f'file_{self.channel_id}.{file_format.split("/")[-1]}'
                file = ContentFile(base64.b64decode(file_str), name=file_name)
                # Process file if needed

            self.handle_new_message(data_json)
    def handle_message_update(self, data_json):
        print('hi i am inside the update')
        message_id = data_json.get("msg_id") 
        updated_message = data_json.get("content")  
        channel_id = data_json.get("channel_id")
        user_id=data_json.get("user_id")
        if not message_id or not updated_message:
            return
        update_response = self.update_message_backend(channel_id, message_id,updated_message)
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
                "message_data": update_response['data'],
            })
            response=self.call_channel_subscription_api(recipient_id_str)
            if recipient_id_str != str(user_id):
                personal_group_name = f"user_notifications_{recipient_id_str}"

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
                "event": "update_message",
                "message": event.get("message", ""),
                "channel_id": event.get("channel_id", ""),
                "message_data": event.get("message_data", {})
            })
        )
    
    def handle_new_message(self, data_json):
        print('i am in new message')
        try:
            async_to_sync(self.channel_layer.group_send)(
            f"channel_chat_{data_json['channel_id']}",
            {
                "type": "chat_message",
                "message_data": data_json,
            }
        )
        except Exception as e:
            self.send_error_message(self.channel_name, f"Error sending message to group: {e}")
            return 

        try:
            response = self.call_get_subscription_api(data_json['channel_id'])
        except Exception as e:
            self.send_error_message(self.channel_name, f"Error calling subscription API: {e}")
            return  

        try:
      
            response_message = self.create_message(data_json['channel_id'], data_json['message'], data_json['sender_id'])
        except Exception as e:
            self.send_error_message(self.channel_name, f"Error creating message: {e}")
            return 

        for recipient in response['data']:
            try:
                recipient_id_str = str(recipient['recipient'])
                personal_group_name = f"user_notifications_{recipient_id_str}"
                async_to_sync(self.channel_layer.group_send)(
                personal_group_name,
                {
                    "type": "new_message_received",
                    "message": "sent you a message",
                    "channel_id": data_json['channel_id'],
                    "message_data": response_message,
                }
            )
                try:
                    recipient_subscription_response = self.call_channel_subscription_api(recipient_id_str)
                except Exception as e:
                    self.send_error_message(personal_group_name, f"Error calling channel subscription API for recipient {recipient_id_str}: {e}")
                    continue
                if recipient_id_str != str(data_json['sender_id']):
                    personal_group_name = f"user_notifications_{recipient_id_str}"
                    async_to_sync(self.channel_layer.group_send)(
                    personal_group_name,
                    {
                    'type': 'send_dm_list',
                    'message': {
                        "event": "send_dm_list",
                        "data": recipient_subscription_response['data']
                        }
                    }
                )
            except Exception as e:
                self.send_error_message(personal_group_name, f"Error processing recipient {recipient_id_str}: {e}")
                continue 
    

    
    def delete_channel_handle(self,data_json):
        channel_id = data_json.get("channel_id")
        token = data_json.get("token")
        user_id = str(data_json.get("user_id"))
        personal_group_name = f"user_notifications_{user_id}"
        try:
            response = self.call_get_subscription_api(channel_id)
        except Exception as e:
            self.send_error_message(personal_group_name, "Error calling subscription API")
            return  

        for recipient in response['data']:
            recipient_id_str = str(recipient['recipient'])
            personal_group_name = f"user_notifications_{recipient_id_str}"
            async_to_sync(self.channel_layer.group_send)(
                personal_group_name,
                {
                    "type": "delete_channel",
                    "message": "Channel deleted successfully",
                    "channel_id": data_json['channel_id'],
                }
            )
        response=self.call_delete_channel(channel_id,token)
        
    def delete_channel(self, event):
        """
        This method handles the delete message event.
        It sends the delete message data to the WebSocket client.
        """
        self.send(
            text_data=json.dumps({
                
                "event":"delete_channel",
                "channel_id": event["channel_id"],
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
                "event":"chat_message",
                "message": event["message"],
                "channel_id": event["channel_id"],
                "message_data": event["message_data"]
            })
        )     
        
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
                (f"Failed to subscribe: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            (f"Error while calling channel subscription API: {e}")
        
    
    def create_message(self,channel_id, message, sender):
        base_url = settings.BACKEND_SERVER_URL
        endpoint = f"{base_url}/api/v1/messages/"
    
        payload = {
        "channel_id": channel_id,
        "message": message,
        "sender": sender
    }
        try:
            response = requests.post(endpoint, json=payload)
        
            if response.status_code == 200:
                json_response = response.json()
                return json_response
            else:
                print(f"Failed to create message: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error while calling message creation API: {e}")
            
    def update_message_backend(self,channel_id, message_id, content):
        base_url = settings.BACKEND_SERVER_URL
        endpoint = f"{base_url}/api/v1/store_msg/update-msg/?channel_id={channel_id}"
    
        payload = {
       "msg_id": message_id,
       "content":content
       }
        try:
            response = requests.put(endpoint, json=payload)
        
            if response.status_code == 200:
                json_response = response.json()
                return json_response
            else:
                print(f"Failed to create message: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error while calling message creation API: {e}")
            
    def call_delete_channel(self,channel_id,token):
        base_url = settings.BACKEND_SERVER_URL
        endpoint = f"{base_url}/api/v1/chat/channels/{channel_id}/"
        headers = {
            'Authorization': f'token {token}'
        }
        
        try:
            response = requests.delete(endpoint,headers=headers)
            if response.status_code == 204:
                return "Channel deleted successfully"
            else:
                return response
        except requests.exceptions.RequestException as e:
            print(f"Error while calling channel deletion API: {e}")

    # def send_error_message(self, event):
    #     self.send(
    #         text_data=json.dumps({
                
    #             "event":"error",
    #             "message": event["message"],
    #         })
    #     )
    # def handle_send_error_message(self,message):
    #     """
    #     Handle'send_error_message' type messages.
    #     Send the error message to the WebSocket client.
    #     """
    #     self.send(
    #         text_data=json.dumps({
    #             "event":"error",
    #             "message": message,
    #         })
    #     )
    def send_error_message(self, channel_name, message):
        error_message = {
        "type": "error",
        "message": message,
    }
        async_to_sync(self.channel_layer.send)(channel_name, error_message)

        
        
        
        
