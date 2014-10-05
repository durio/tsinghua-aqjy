#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import *

import mechanize
import re

br = mechanize.Browser()
library = {}

PASSWORD_RE = re.compile(ur'document\.getElementById\("password"\)\.value = \'(.*?:null)\';')
LIBRARY_RE = re.compile(ur'<tr style="border: 0;">\s*<td style="border: 0;">\s*(\d+)&nbsp;&nbsp;\s*(单选题|多选题|判断题)\s*</td>\s*'
        + ur'<td style="border: 0;"><a title="查看详细" href="/exam/studenttest/studentTestAction!gotoSearchThemeOneDetail\.do\?themeid=(\d+)" target="_blank">(.*?)</a></td>\s*</tr>'
        + ur'.*?<tr>\s*<td colspan="3"><a id="da_\d+" class="da" href="javascript: getDaan\(\'da_\d+\'\);">正确答案：</a>\s*'
        + ur'<font id="an_\d+" class="an" color="red" style="display: none;">\s*(\S+)\s*</font>\s*</td>\s*</tr>', re.DOTALL)
QUESTION_RE = re.compile(ur'题干： (.*?)\(分数：\d+分\)', re.DOTALL)

def scrap_library_page(page):
    count = 0
    for nr, qtype, qid, qtext, qans in LIBRARY_RE.findall(page):
        if qtype == u'单选题':
            library[qtext] = qans
        elif qtype == u'多选题':
            library[qtext] = qans.split(u',')
        elif qtype == u'判断题' and qans in (u'对', u'错'):
            library[qtext] = 'A' if qans == u'对' else 'B'
        else:
            continue
        count += 1
    print count, 'question(s) loaded.'

# Log in
print 'Initializing'
br.open('http://aqjy.tsinghua.edu.cn/')
print 'Logging in 1/2'
br.select_form(predicate=(lambda form: form.attrs.get('id') == 'loginForm'))
br['username'] = USER_ID
br['password'] = USER_PASSWORD
br.submit()

print 'Logging in 2/2'
br.select_form(nr=0)
br.set_all_readonly(False)
br['j_username'] = USER_ID
br['j_password'] = PASSWORD_RE.search(br.response().read().decode('gb18030', 'replace')).group(1)
br.submit()

# Load library
count = 0
for library_id in LIBRARY_IDS:
    count += 1
    print 'Loading library %d/%d: %s' % (count, len(LIBRARY_IDS), library_id)
    br.open('http://aqjy.tsinghua.edu.cn/exam/studenttest/studentTestAction!gotoSearchTheme.do?knowid='
            + library_id + '&deptId=0')
    scrap_library_page(br.response().read().decode('gb18030', 'replace'))

# Answer
print 'Loading exam 1/4'
br.open('http://aqjy.tsinghua.edu.cn/exam/studentexame/studentExameAction!getExame.do')
print 'Loading exam 2/4'
br.open('http://aqjy.tsinghua.edu.cn/exam/studentexame/studentExameAction!beforeGotoExame.do?exameid=' + EXAM_ID)
print 'Loading exam 3/4'
# In some exams, there is a "foreword" page here. Let's be bold and go one step further.
# With some tests, it appears there's no harm in exams without such a page.
br.open('http://aqjy.tsinghua.edu.cn/exam/studentexame/studentExameAction!gotoExame.do?exameid=' + EXAM_ID)
questions = max(map(int, re.findall(ur'javascript:formsubmit\(\'(\d+)\'\)', br.response().read().decode('gb18030', 'replace'))))

print 'Loading exam 4/4'
br.select_form('exameform')
br.set_all_readonly(False)
br['pageNum'] = '1'
br.submit()

answer_nr = 1
while answer_nr <= questions:
    question = QUESTION_RE.search(br.response().read().decode('gb18030', 'replace')).group(1)
    print 'Answering %d/%d: %s' % (answer_nr, questions, question)
    answer = library[question]
    br.select_form('exameform')
    if isinstance(answer, basestring):
        br['answerradio'] = [answer]
    else:
        br['answercheckbox'] = answer
    br.set_all_readonly(False)
    br['pageNum'] = str(answer_nr + 1)
    answer_nr += 1
    br.submit()

print 'Finished'
