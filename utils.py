from random import choice, randint

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from emoji import emojize
from telegram import KeyboardButton, ReplyKeyboardMarkup

import config
import settings


def main_keyboard():
    send_location = KeyboardButton('Мои координаты', request_location=True)
    return ReplyKeyboardMarkup([['Пришли слоника', send_location]])


def set_cities_set(context):
    context.user_data['bot_cities'] = config.CITIES_SET
    context.user_data['user_cities'] = set()


def get_smile(user_data):
    # context.user_data - dict for the user data while the bot is running
    if 'emoji' not in user_data:
        smile = choice(config.EMOJI_LIST)
        user_data['emoji'] = emojize(smile, language='alias')
    return user_data['emoji']


def precalculate(part):
    if type(part) is str:
        if '*' in part:
            result = 1
            for subpart in part.split('*'):
                result *= precalculate(subpart)
            return result
        elif '/' in part:
            parts = list(map(precalculate, part.split('/')))
            result = parts[0]
            for subpart in parts[1:]:
                result /= subpart
            return result
        else:
            return float(part)
    elif type(part) is list:
        for i in range(len(part)):
            part[i] = precalculate(part[i])
        return part[0] - sum(part[1:])


def play_random_numbers(user_int):
    bot_int = randint(user_int - 10, user_int + 10)
    if user_int > bot_int:
        message = f'Ты загадал {user_int}, я загадал {bot_int}, ты выиграл!'
    elif user_int == bot_int:
        message = f'Ты загадал {user_int}, я загадал {bot_int}, ничья!'
    else:
        message = f'Ты загадал {user_int}, я загадал {bot_int}, я выиграл!'
    return message


def has_object_on_image(file_name, object_name):
    # Construct the communications channel
    channel = ClarifaiChannel.get_grpc_channel()
    # Construct the V2Stub object for accessing the Clarifai API functionality
    stub = service_pb2_grpc.V2Stub(channel)
    # Set up the metadata object that's used to authenticate.
    # This authorization will be used by every Clarifai API call.
    metadata = (('authorization', 'Key ' + settings.CLARIFAI_API_KEY),)

    with open(file_name, 'rb') as f:
        file_bytes = f.read()
        # Translates the opened file to base64
        # base64 is the format that Clarifai expects to receive
        image = resources_pb2.Image(base64=file_bytes)

    request = service_pb2.PostModelOutputsRequest(
        model_id='general-image-recognition',
        inputs=[resources_pb2.Input(data=resources_pb2.Data(image=image))]
    )
    response = stub.PostModelOutputs(request, metadata=metadata)
    return check_response_for_object(response, object_name)


def check_response_for_object(response, object_name):
    if response.status.code == status_code_pb2.SUCCESS:
        # Response is a dict, outputs is a list of responses dcts for requests
        # Take the first response
        output = response.outputs[0]
        # Iterate through the concept objects
        for concept in output.data.concepts:
            if concept.name == object_name and concept.value >= 0.9:
                return True
    else:
        print(f'Ошибка распознавания картинки: {response.status.description}')
    return False
