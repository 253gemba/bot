import requests


async def translate_audio_to_rus(audio):
    # audio = 'voice/file_23.ogg'
    # uri = 'https://api.wit.ai/speech?v=20170307'
    uri = 'https://asr.nanosemantics.ai/asr/'
    # uri = 'https://httpbin.org'
    api_key = '5WSXQ7QWMCKETS4AOZ3UL63LNILND3YV'
    # client = Wit(api_key)
    # os.environ['WIT_API_VERSION'] = '20170307'
    response = None
    with open(audio, 'rb') as f:
        # response = client.speech(f, {'Content-Type': 'audio/ogg;encoding=signed-integer;bits=16;rate=16000;endian=little'})
        # print(response)
        # response = requests.post(
        #     uri,
        #     headers={
        #         'Authorization': f"Bearer {api_key}",
        #         'Content-Type': 'audio/ogg',
        # 'cache-control': 'no-cache',
        #     },
        #     data=f.read()
        # )
        form_data = {
            "model_type": "ACR",
            "filename": "67006370772"
        }
        files = {
            'audio_blob': ('blob', f, 'audio/webm;codecs=opus'),
            'model_type': 'ACR',
            'filename': '67006370772',
            'user_id': '128885673',
        }
        response = requests.post(
            uri,
            headers={
                'Authorization': f"Basic YW5uOjVDdWlIT0NTMlpRMQ=="
            },
            files=files,
            data=form_data
        )
    response = response.json()['r']
    if response:
        return response[0]['response'][0]['text']
    return None
