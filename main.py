from api_helper import VkFotoDownloader, YandexUploader

if __name__ == '__main__':
	TOKEN_VK = ''
	ID_VK = ''
	TOKEN_YANDEX = ''

	Vk = VkFotoDownloader(ID_VK, TOKEN_VK)
	Ya = YandexUploader(TOKEN_YANDEX)

	# creates log with photos' names and sizes, saves it on PC-storage
	print(Vk.set_log_json())

	# creates directory in Yandex.disk and uploads into it all photo
	# directly from profile album (default) of VK User
	Ya.upload_directly(Vk.owner_id, Vk.get_photos_list())
	print(Ya.path_dir(Vk.owner_id))

	# uploads log file into Yandex.disk in addition to photos
	Ya.uploading_from_hdd('log.json', Vk.owner_id)
