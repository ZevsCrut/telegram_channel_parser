import json
from datetime import datetime
import os

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

api_id = 123456 #ur api id as integer
api_hash = 'ur tg api_hash'
username = 'phone number in international format'

client = TelegramClient(username, api_id, api_hash,system_version='4.16.30-vxCUSTOM')
client.start()

async def dump_all_messages(channel,name,order):
	"""Writes a json file with information about all messages in the channel/chat."""
	offset_msg = 0  # The number of the record from which reading starts.
	limit_msg = 100  # The maximum number of records transmitted at one time.

	all_messages = []  # A list of all messages.
	total_messages = 0
	total_count_limit = 0  # Change this value if you don't need all the messages.

	class DateTimeEncoder(json.JSONEncoder):
		def default(self, o):
			if isinstance(o, datetime):
				return o.isoformat()
			if isinstance(o, bytes):
				return list(o)
			return json.JSONEncoder.default(self, o)

	while True:
		history = await client(GetHistoryRequest(
			peer=channel,
			offset_id=offset_msg,
			offset_date=None, add_offset=0,
			limit=limit_msg, max_id=0, min_id=0,
			hash=0))
		if not history.messages:
			break
		messages = history.messages
		for message in messages:
			all_messages.append(message.to_dict())
		offset_msg = messages[len(messages) - 1].id
		total_messages = len(all_messages)
		if total_count_limit != 0 and total_messages >= total_count_limit:
			break


	os.mkdir(f'{order}.{name}')
	os.chdir(f'{order}.{name}')

	with open(f'detailed_{name}.json', 'w', encoding='utf8') as outfile:
		 json.dump(all_messages, outfile, ensure_ascii=False, cls=DateTimeEncoder)

	with open(f'detailed_{name}.json', 'r', encoding='utf8') as raw_file:
		data = json.load(raw_file)
		new_file_data = []
		for i in data:
			if i['_'] == 'Message':
				msg_data = {}
				msg_data['message_id'] = i['id']
				msg_data['date'] = i['date']
				msg_data['text'] = i['message']
				if i['media'] == None:
					msg_data['is_media'] = 0
				else:
					msg_data['is_media'] = 1
				new_file_data.append(msg_data)

		with open(f'correct_{name}.json', 'w') as new_file:
			json.dump(new_file_data, new_file)
	os.chdir('..')
	print('amount of messages: ',total_messages)

async def main():
	with open('channels.txt','r') as file:
		chanels = file.readlines()
		print('amount of channels in txt: ',len(chanels))
		order = 0
		os.chdir('result')
		for url in chanels:
			order += 1
			channel_name = str(url[13:])
			print('------------------------------------')
			print('channel url: ',url)
			print('start parsing')

			channel = await client.get_entity(url)
			await dump_all_messages(channel,channel_name,order)


with client:
	client.loop.run_until_complete(main())