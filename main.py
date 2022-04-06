import pip

import requests

import os

from progress.bar import IncrementalBar

import json

from datetime import datetime

from pprint import pprint


def normal_date(date: int) -> str:
	current_date = str(datetime.utcfromtimestamp(date)).split(' ')[0]
	return current_date


def max_size(list_of_sizes: list) -> dict:
	return list_of_sizes[-1]


def get_path() -> str:
	return os.getcwd()


class VkFotoDownloader:

	def __init__(self, vk_id, token):
		self.owner_id = vk_id
		self.token = token
		self.albums = ['profile', 'wall', 'saved']
		self.url = 'https://api.vk.com/method/'

	def duplicates_name(self, list_of_photos):
		dict_of_names = {}
		for photo in list_of_photos:
			if photo['name'] not in dict_of_names.keys():
				dict_of_names.update({f'{photo["name"]}': 1})
			else:
				dict_of_names[f'{photo["name"]}'] += 1
		list_of_names = []
		for name in dict_of_names:
			if dict_of_names[name] > 1:
				list_of_names += [name]
		for photo in list_of_photos:
			if photo['name'] in list_of_names:
				photo['name'] = f'{photo["name"][:-4]}_{photo["date"]}.jpg'

	def get_photos_list(self, owner_id=None, version=5.131, album_id='profile') -> list:
		resp = requests.get(f'{self.url}photos.get', params={'access_token': self.token,
															 'v': version,
															 'owner_id': owner_id,
															 'album_id': album_id,
															 'photo_sizes': 1,
															 'extended': 1
															 })
		list_of_photos = []
		bar = IncrementalBar('Creating list of photos', max=len(resp.json()['response']['items']))
		for photo in resp.json()['response']['items']:
			bar.next()
			list_of_photos += [{'name': f'{photo["likes"]["count"]}.jpg',
							   'date': photo['date'],
							   'size_type': max_size(photo['sizes'])['type'],
							   # 'width': max_size(photo['sizes'])['width'],
							   # 'height': max_size(photo['sizes'])['height'],
							   'url': max_size(photo['sizes'])['url']
							   }]
		self.duplicates_name(list_of_photos)
		bar.finish()
		return list_of_photos

	# creates .json file {"file_name": , "size":)
	def set_log_json(self) -> str:
		list_photos_cutted = []
		for photo in self.get_photos_list():
			list_photos_cutted += [{'file_name': photo["name"], 'size': photo["size_type"]}]
		with open(f'{get_path()}/upload/log.json', 'w+') as file:
			json.dump(list_photos_cutted, file, indent=2)
		return 'Log created'


class YandexUploader:

	def __init__(self, token):
		self.token = f'OAuth {token}'

	def get_href(self, file_name, path_dir) -> str:
		resp = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload',
								headers={'Authorization': self.token},
								params={'path': f'{path_dir}/{file_name}', 'overwrite': 'true'})
		return resp.json()['href']

	def path_dir(self, dir_name):
		resp = requests.put('https://cloud-api.yandex.net/v1/disk/resources',
							headers={'Authorization': self.token},
							params={'path': f'/free/photo_{dir_name}'})
		return f'/free/photo_{dir_name}'

	def uploading_from_hdd(self, file_name, dir_name):
		file_path = f'{os.getcwd()}\\upload\\{file_name}'
		with open(file_path, 'r') as file:
			data = json.load(file)
			requests.put(self.get_href(file_name, self.path_dir(dir_name)), data=data)
		return "Done"

	def upload_directly(self, Vk_object: VkFotoDownloader, album='profile'):
		path_name = self.path_dir(Vk_object.owner_id)
		list_of_photos = Vk_object.get_photos_list(album_id=album)
		bar = IncrementalBar('Progress...', max=len((list_of_photos)))
		for photo in list_of_photos:
			bar.next()
			resp = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
								headers={'Authorization': self.token},
								params={'path': path_name,
										'url': photo['url']
										}
								)
		bar.finish()
		return 'Done'


class GoogleUploader:

	def __init__(self):
		pass

	def uploading(self):
		pass


if __name__ == '__main__':
	TOKEN_VK = ''
	ID_VK = ''
	TOKEN_YANDEX = ''


	Vk = VkFotoDownloader(ID_VK, TOKEN_VK)
	Ya = YandexUploader(TOKEN_YANDEX)

	Vk.set_log_json()

	Ya.upload_directly(Vk)
	Ya.uploading_from_hdd('log.json', Vk.owner_id)