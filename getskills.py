#!/usr/bin/python3
# -*- coding: utf-8 -*-
#pip install beautifulsoup4
#pip install html5lib
from urllib.request import urlopen,urlretrieve
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import os,re,json,sys

class FF14skills:

    def __init__(self):
        self.jobClasses = [
            {
                'class':'tank',
                'name':'tank',
                'order':1
            },
            {
                'class':'healer',
                'name':'healer',
                'order':2,
            },
            {
                'class':'meleeDps',
                'name':'melee dps',
                'order':3
            },
            {
                'class':'phyRangedDps',
                'name':'physical ranged dps',
                'order':4
            },
            {
                'class':'magRangedDps',
                'name':'magical ranged dps',
                'order':5
            }
        ]
        self.jobClassesDict = {c['class']:c for c in self.jobClasses}
        self.jobs = [
            #healers
            {
                'job':'whitemage',
                'class':'healer',
                'weburl': 'whitemage',
                'name':'White Mage',
                'name_short':'whm',
                'name_cn':'白魔法师',
                'name_short_cn':'白魔,白',
                'order':1,
            },
            {
                'job':'scholar',
                'class':'healer',
                'weburl': 'scholar',
                'name':'Scholar',
                'name_short':'sch',
                'name_cn':'学者',
                'name_short_cn':'学者,学',
                'order':2,
            },
            {   
                'job':'astrologian',
                'class':'healer',
                'weburl': 'astrologian',
                'name':'Astrologian',
                'name_short':'ast',
                'name_cn':'占星术师',
                'name_short_cn':'占星,占',
                'order':3,
            },
            #tanks
            {
                'job':'paladin',
                'class':'tank',
                'weburl':'paladin',
                'name':'paladin',
                'name_short':'pld',
                'name_cn':'骑士',
                'name_short_cn':'骑士,骑',
                'order':4,
            },
            {
                'job':'warrior',
                'class':'tank',
                'weburl':'warrior',
                'name':'warrior',
                'name_short':'war',
                'name_cn':'战士',
                'name_short_cn':'战士,战',
                'order':5
            },
            {
                'job':'darkknight',
                'class':'tank',
                'weburl':'darkknight',
                'name':'darkknight',
                'name_short':'drk',
                'name_cn':'暗黑骑士',
                'name_short_cn':'黑骑',
                'order':6
            },
            #melee dps
            {
                'job':'monk',
                'class':'meleeDps',
                'weburl':'monk',
                'name':'monk',
                'name_short':'mnk',
                'name_cn':'武僧',
                'name_short_cn':'僧',
                'order':7
            },
            {
                'job':'dragoon',
                'class':'meleeDps',
                'weburl':'dragoon',
                'name':'dragoon',
                'name_short':'drg',
                'name_cn':'龙骑士',
                'name_short_cn':'龙骑,龙',
                'order':8
            },
            {
                'job':'ninja',
                'class':'meleeDps',
                'weburl':'ninja',
                'name':'ninja',
                'name_short':'nin',
                'name_cn':'忍者',
                'name_short_cn':'忍',
                'order':9
            },
            {
                'job':'samurai',
                'class':'meleeDps',
                'weburl':'samurai',
                'name':'samurai',
                'name_short':'sam',
                'name_cn':'武士',
                'name_short_cn':'侍',
                'order':10
            },
            # ranged
            {
                'job':'bard',
                'class':'phyRangedDps',
                'weburl':'bard',
                'name':'bard',
                'name_short':'brd',
                'name_cn':'诗人',
                'name_short_cn':'诗',
                'order':11
            },
            {
                'job':'machinist',
                'class':'phyRangedDps',
                'weburl':'machinist',
                'name':'machinist',
                'name_short':'mch',
                'name_cn':'机工士',
                'name_short_cn':'机工,机',
                'order':12
            },
            {
                'job':'blackmage',
                'class':'magRangedDps',
                'weburl':'blackmage',
                'name':'blackmage',
                'name_short':'blm',
                'name_cn':'黑魔法师',
                'name_short_cn':'黑魔,黑',
                'order':13
            },
            {
                'job':'summoner',
                'class':'magRangedDps',
                'weburl':'summoner',
                'name':'summoner',
                'name_short':'smn',
                'name_cn':'召唤师',
                'name_short_cn':'召唤,召',
                'order':14
            },
            {   
                'job':'redmage',
                'class':'magRangedDps',
                'weburl':'redmage',
                'name':'redmage',
                'name_short':'rdm',
                'name_cn':'赤魔法师',
                'name_short_cn':'赤魔,赤',
                'order':15
            },
        ]
        self.jobClassSkills= {}    # 职能技能
        
    def getWebpageUrl(self,placeholder):
        url = 'http://act.ff.sdo.com/project/20170901battle/{}.html'.format(placeholder)
        return url
        
    def extractSkillTableContent(self, jobKey, tableContent, idPrefix=''):
        skillsOfType = []
        skillsOfTypeSaved = {}
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
            if id in skillsOfTypeSaved:
                print('{}: skill id {} exist! {}'.format(jobKey, id, skillsOfTypeaved[id]))
            skillsOfTypeSaved[id] = skill
            skillsOfType.append(skill)
        return skillsOfType
        
    def analyzeJob(self,job):
        print('-'*20)
        jobKey = job['job']
        print('processing: '+jobKey)
        obj = BeautifulSoup(urlopen(self.getWebpageUrl(job['weburl'])), 'html5lib')
        tempContent = obj('div',class_=['js__select--pve','job__content--battle'])
        res = {'skillTypes':[], 'job':job}
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
                        jobClass = job['class']
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
                        res['skillTypes'].append({'name':h3Name, 'skills':skillsOfType})
                        print('{} handled with type "{}".'.format(h3Name, idPrefix))
                else:
                    # no h3 means 职业量普
                    pass
                    
        return res     
        
    def analyzeAll(self):
        res = [self.analyzeJob(j) for j in self.jobs]
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
        if len(self.jobClassSkills) == 0:
            self.analyzeAll()
        filePath = os.path.join(self.getPath('skilljs'), 'jobClassSkills.js')
        self.saveToFile(self.jobClassSkills, filePath)
        print('jobClassSkill file saved as '+filePath)
        return self.jobClassSkills
        
    def saveJobSkillsToFile(self):
        skills = self.analyzeAll()
        filePath = os.path.join(self.getPath('skilljs'), 'jobSkills.js')
        self.saveToFile(skills,filePath)
        print('jobSkill file saved as '+filePath)
        return skills
        
    def saveJobClassesToFile(self):
        classes = self.getJobClasses()
        filePath = os.path.join(self.getPath('skilljs'), 'jobClasses.js')
        self.saveToFile(classes, filePath)
        print('jobClasses file saved as '+filePath)
        return classes
        
    def saveToFile(self, content, path, encoding='utf8'):
        with open(path, 'w', encoding=encoding) as f:
            f.write('module.exports = ');
            f.write(json.dumps(content, ensure_ascii=False))
        
    def getJobClasses(self):
        res = []
        for cls in self.jobClasses:
            cls['jobs'] = [job for job in self.jobs if job['class']==cls['class']]
            cls['iconFilePath'] = '/resources/jobicons/{}.png'.format(cls['class'])
            res.append(cls)
        return res
        
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
    if len(sys.argv)==1:
        usage = '''
Usage:
    python ./getSkills.py (all/skills/classskills/classes)
        '''
        print(usage)
        sys.exit(0)
    x = FF14skills()
    for param in sys.argv:
        param = param.lower()
        if param in ['all', 'skills']:
            x.saveJobSkillsToFile()
        if param in ['all', 'classskills']:
            x.saveJobClassSkillsToFile()
        if param in ['all', 'classes']:
            x.saveJobClassesToFile()
    #x.saveJobSkillsToFile()
    #x.saveJobClassSkillsToFile()
    #x.saveJobClassesToFile()
    #print(x.getJobClasse())