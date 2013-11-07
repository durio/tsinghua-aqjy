tsinghua-aqjy
=============

Script for taking an exam on http://aqjy.tsinghua.edu.cn/

Users need to create a `config.py` manually, with contents below:

	EXAM_ID = '<exam id>'
	LIBRARY_IDS = ['343181', '343732', '53453', '343589', '344072', '53342']
	USER_ID = '<student id>'
	USER_PASSWORD = '<student password>'

Replace everything in angle brackets with your own values.

After the script finishes, the exam paper is not submitted automatically.

You can either submit it manually, or wait for it to expire.
