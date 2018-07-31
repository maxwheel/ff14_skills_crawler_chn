#!/usr/bin/python3
# -*- coding: utf-8 -*-
#pip install beautifulsoup4
#pip install html5lib
from urllib.request import urlopen,urlretrieve
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import os,re,json

class FF14skills:

    def __init__(self):
        self.jobClasses = {
            'tank':{
                'name':'tank'
            },
            'healer':{
                'name':'healer'
            },
            'meleeDps':{
                'name':'melee dps'
            },
            'phyRangedDps':{
                'name':'physical ranged dps'
            },
            'magRangedDps':{
                'name':'magical ranged dps'
            }
        }
        self.jobs = {
            #healers
            'whitemage':{
                'class':'healer',
                'weburl': 'whitemage',
                'name':'White Mage',
                'name_short':'whm',
                'name_cn':'白魔法师',
                'name_short_cn':'白魔,白'
            },
            'scholar':{
                'class':'healer',
                'weburl': 'scholar',
                'name':'Scholar',
                'name_short':'sch',
                'name_cn':'学者',
                'name_short_cn':'学者,学'
            },
            'astrologian':{
                'class':'healer',
                'weburl': 'astrologian',
                'name':'Astrologian',
                'name_short':'ast',
                'name_cn':'占星术师',
                'name_short_cn':'占星,占'
            },
            #tanks
            'paladin':{
                'class':'tank',
                'weburl':'paladin',
                'name':'paladin',
                'name_short':'pld',
                'name_cn':'骑士',
                'name_short_cn':'骑士,骑'
            },
            'warrior':{
                'class':'tank',
                'weburl':'warrior',
                'name':'warrior',
                'name_short':'war',
                'name_cn':'战士',
                'name_short_cn':'战士,战'
            },
            'darkknight':{
                'class':'tank',
                'weburl':'darkknight',
                'name':'darkknight',
                'name_short':'drk',
                'name_cn':'暗黑骑士',
                'name_short_cn':'黑骑'
            },
            #melee dps
            'monk':{
                'class':'meleeDps',
                'weburl':'monk',
                'name':'monk',
                'name_short':'mnk',
                'name_cn':'武僧',
                'name_short_cn':'僧'
            },
            'dragoon':{
                'class':'meleeDps',
                'weburl':'dragoon',
                'name':'dragoon',
                'name_short':'drg',
                'name_cn':'龙骑士',
                'name_short_cn':'龙骑,龙'
            },
            'ninja':{
                'class':'meleeDps',
                'weburl':'ninja',
                'name':'ninja',
                'name_short':'nin',
                'name_cn':'忍者',
                'name_short_cn':'忍'
            },
            'samurai':{
                'class':'meleeDps',
                'weburl':'samurai',
                'name':'samurai',
                'name_short':'sam',
                'name_cn':'武士',
                'name_short_cn':'侍'
            },
            # ranged
            'bard':{
                'class':'phyRangedDps',
                'weburl':'bard',
                'name':'bard',
                'name_short':'brd',
                'name_cn':'诗人',
                'name_short_cn':'诗'
            },
            'machinist':{
                'class':'phyRangedDps',
                'weburl':'machinist',
                'name':'machinist',
                'name_short':'mch',
                'name_cn':'机工士',
                'name_short_cn':'机工,机'
            },
            'blackmage':{
                'class':'magRangedDps',
                'weburl':'blackmage',
                'name':'blackmage',
                'name_short':'blm',
                'name_cn':'黑魔法师',
                'name_short_cn':'黑魔,黑'
            },
            'summoner':{
                'class':'magRangedDps',
                'weburl':'summoner',
                'name':'summoner',
                'name_short':'smn',
                'name_cn':'召唤师',
                'name_short_cn':'召唤,召'
            },
            'redmage':{
                'class':'magRangedDps',
                'weburl':'redmage',
                'name':'redmage',
                'name_short':'rdm',
                'name_cn':'赤魔法师',
                'name_short_cn':'赤魔,赤'
            },
        }
        self.jobClassSkills = {}    # 职能技能
        
    def getWebpageUrl(self,jobKey):
        url = 'http://act.ff.sdo.com/project/20170901battle/{}.html'.format(self.jobs[jobKey]['weburl'])
        return url
        
    def extractSkillTableContent(self, jobKey, tableContent, idPrefix=''):
        skillsOfType = {}
        skillTrs = tableContent.find('tbody')('tr')
        # save skills
        nextID = 0
        for skillTr in skillTrs:
            id = idPrefix
            if 'id' in skillTr.attrs:
                id += ''.join([i for i in skillTr['id'] if i.isdigit()])
            else:
                nextID += 1
                id += str(nextID)
            skill = {'id':id}
            for td in skillTr('td'):
                if 'class' not in td.attrs: continue    # skip TDs without class
                cls = td['class'][0]
                if cls == 'skill':
                    iconSrc = td.find('img')['src']
                    # skill['icon'] = iconSrc
                    iconFile = self.handleIcon(iconSrc, jobKey)
                    if iconFile: skill['iconFile'] = iconFile
                    skill['name'] = td.find('p').find('strong').get_text()
                elif cls in ['classification', 'cast', 'recast']:
                    skill[cls] = td.get_text()
                elif cls == 'content':
                    skill[cls] = [s for s in td.strings]
                else:
                    pass
            if id in skillsOfType:
                print('{}: skill id {} exist! {}'.format(jobKey, id, skillsOfType[id]))
            skillsOfType[id] = skill
        return skillsOfType
        
    def analyzeJob(self,jobKey):
        print('-'*20)
        print('processing: '+jobKey)
        obj = BeautifulSoup(urlopen(self.getWebpageUrl(jobKey)), 'html5lib')
        tempContent = obj('div',class_=['js__select--pve','job__content--battle'])
        res = {'skills':[], 'jobkey':jobKey}
        for item in tempContent:
            skillContents = item('div',class_='job__content__wrapper')
            # get update date
            updatedAt = item.find('p', class_='job__update')
            if updatedAt:
                updatedAt = updatedAt.get_text()
                search = re.search('(\d{4})\D{0,1}(\d{1,2})\D{0,1}(\d{1,2})', updatedAt)
                if search:
                    updatedAt = '/'.join(search.groups())
                res['updatedAt'] = updatedAt
                print('{} skills updated at: {}'.format(jobKey, updatedAt))
            # handle all type of skills
            skillType = ord('a') # set the number of skill type as a prefix
            for skillContent in skillContents:
                h3 = skillContent.find('h3', class_='job__sub_title')
                if h3:
                    h3Name = h3.get_text() 
                    if h3Name == '职能技能':
                        # handle 职能技能 which is not saved yet
                        jobClass = self.jobs[jobKey]['class']
                        if jobClass not in self.jobClassSkills:
                            jobClassSkills = self.extractSkillTableContent(jobClass, skillContent, jobClass)
                            self.jobClassSkills[jobClass] = jobClassSkills
                    elif h3Name == '特性':
                        # skil 特性
                        pass
                    else:
                        # save skill types
                        idPrefix = ''
                        if h3Name != '专用技能':
                            idPrefix = chr(skillType)
                            skillType += 1
                        skillsOfType = self.extractSkillTableContent(jobKey, skillContent, idPrefix)
                        res['skills'].append({'name':h3Name, 'value':skillsOfType})
                        print('{} handled with type "{}".'.format(h3Name, idPrefix))
                else:
                    # no h3 means 职业量普
                    pass
                    
        return res     
        
    def analyzeAll(self):
        res = {j:self.analyzeJob(j) for j in self.jobs}
        return res
        
    def getPath(self, type, getAbspath=False):
        cur = getAbspath and os.path.abspath(os.curdir) or os.curdir
        if type == 'skillicons':
            return os.path.join(cur, 'resources', 'skillicons')
        elif type == 'skilljs':
            return os.path.join(cur, 'resources')
        else:
            print('Type "{}" not defined!'.format(type))
            raise Exception('error')
    
    def saveJobClassSkillsToFile(self):
        print('saveJobClassSkillsToFile.........')
        filePath = os.path.join(self.getPath('skilljs'), 'jobClassSkills.js')
        with open(filePath, 'w', encoding='gbk') as f:
            f.write('jobClassSkills = ')
            f.write(json.dumps(self.jobClassSkills, ensure_ascii=False))
            print('jobClassSkill file saved as '+filePath)
        return self.jobClassSkills
        
    def saveJobSkillsToFile(self):
        print('saveJobSkillsToFile.........')
        skills = self.analyzeAll()
        filePath = os.path.join(self.getPath('skilljs'), 'jobSkills.js')
        with open(filePath, 'w', encoding='gbk') as f:
            f.write('jobSkills = ')
            f.write(json.dumps(skills, ensure_ascii=False))
            print('jobSkill file saved as '+filePath)
        return skills
        
    def handleIcon(self, iconUri, jobKey):
        pattern = '.*\/([a-zA-Z0-9\_\-]+)\.([a-zA-Z]+)$'
        currentPath = self.getPath('skillicons')
        if not os.path.isdir(currentPath):
            os.mkdir(currentPath)
        iconPath = os.path.join(currentPath, jobKey)
        if not os.path.isdir(iconPath):
            os.mkdir(iconPath)
        res = re.match(pattern, iconUri)
        if res:
            iconFileName = '.'.join(res.groups())
            iconFileFullPath = os.path.join(iconPath, iconFileName)
            if not os.path.isfile(iconFileFullPath):
                urlretrieve(iconUri, iconFileFullPath)
                print('{}: {} saved'.format(jobKey,iconFileName))
            return iconFileName
        
if __name__ == '__main__':
    x = FF14skills()
    #([print(item) for item in x.analyzeAll()[0]])
    x.saveJobSkillsToFile()
    x.saveJobClassSkillsToFile()