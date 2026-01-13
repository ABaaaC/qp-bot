import os
import json

from aiogram.types.input_file import FSInputFile

 
# generate file_id's
file_id_dict = {}
for i in range(1, 400):
    screenshot_path = os.getcwd() + '/' + f"screenshots/lottery_number_{i}.png"
    photo = FSInputFile(path=screenshot_path)
    sent_message = await message.answer_photo(photo=photo)
    file_id = sent_message.photo[-1].file_id
    file_id_dict[i] = file_id
    await sent_message.delete()
with open("file_id_dict.json", "w") as outfile:
    json.dump(file_id_dict, outfile, indent=4) 