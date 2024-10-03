import re
from django.conf import settings


class TMSCalculation:
    tms_data = settings.MEDIA_ROOT + "\\" + "tms.txt"
    input_file = open(tms_data, 'r').read().split('\n')
    status = []
    TMS = {}
    rules = {}
    stack = []

    def add_rule(self,stack, orig_rule, pat):
        rule = ""
        while stack:
            item = stack.pop()
            if item == '+':
                if self.rules.get(rule):
                    self.rules[rule].append([pat, orig_rule, False])
                else:
                    self.rules[rule] = [[pat, orig_rule, False]]
                rule = ""
            else:
                if item == '*':
                    item = ','
                rule = item + rule
        if self.rules.get(rule):
            self.rules[rule].append([pat, orig_rule, False])
        else:
            self.rules[rule] = [[pat, orig_rule, False]]

    def assess_rules(self):
        if not self.rules:
            return
        rules_copy = self.rules.copy()
        for key in rules_copy.keys():
            found = True
            for k in key.split(','):
                if not self.TMS.get(k):
                    found = False
            if found:
                r_list = self.rules[key].copy()
                for rule_list in r_list:
                    if not rule_list[2]:
                        rule_list[2] = True
                        str = '{' + key + ',' + rule_list[1] + '}'
                        if self.TMS.get(rule_list[0]):
                            self.TMS[rule_list[0]].append(str)
                        else:
                            self.TMS[rule_list[0]] = [str]
                        self.status.append(rule_list[0] + ':' + str)
        if rules_copy != self.rules:
            self.assess_rules()

    def delete_literals(self,literal):
        deleted = []
        for key in self.rules.keys():
            for k in key.split(','):
                if k == literal:
                    r_list = self.rules[key].copy()
                    for rule_list in r_list:
                        if rule_list[2]:
                            rule_list[2] = False
                            str = '{' + key + ',' + rule_list[1] + '}'
                            if self.TMS.get(rule_list[0]):
                                self.TMS[rule_list[0]].remove(str)
                                deleted.append(rule_list[0])
                                if not self.TMS[rule_list[0]]:
                                    self.TMS.pop(rule_list[0])
                            self.status.remove(rule_list[0] + ':' + str)
        while deleted:
            self.delete_literals(deleted.pop(0))

    def delete_rules(self,rule, literal):
        self.status.remove(rule)

        rules_copy = self.rules.copy()
        for r in rules_copy:
            l_copy = self.rules[r].copy()
            for l in l_copy:
                if l[1] == rule:
                    self.rules[r].remove(l)
        rules_copy = self.rules.copy()
        for r in rules_copy:
            if not rules_copy[r]:
                self.rules.pop(r)

        def delete_recursive(self, r, literal):
            to_delete = literal
            delete_rule = ',' + r + '}'
            status_copy = self.status.copy()
            for i in status_copy:
                if delete_rule in i:
                    self.status.remove(i)
            TMS_list = self.TMS[to_delete].copy()
            for i in TMS_list:
                if delete_rule in i:
                    self.TMS[to_delete].remove(i)
            if not self.TMS[to_delete]:
                self.TMS.pop(to_delete)
                if self.rules.get(to_delete):
                    for i in self.rules[to_delete]:
                        if i[2]:
                            i[2] = False
                            delete_recursive(i[1], i[0])

        delete_recursive(rule, literal)

    def startProcess(self):
        myList =[]
        myList.clear()

        for line in self.input_file:

            if line.startswith('T'):

                # Rule
                pattern = re.search(r'Tell:(([\w+*-]*\w)->(-*\w))', line)
                if pattern:
                    self.status.append(pattern.group(1))
                    for i in pattern.group(2):
                        self.stack.append(i)
                    self.add_rule(self.stack, pattern.group(1), pattern.group(3))
                    self.assess_rules()
                    self.assess_rules()
                    continue

                # Single positive literal
                pattern = re.search(r'Tell:(-*\w)', line)
                if pattern:
                    str = pattern.group(1)
                    if self.TMS.get(str):
                        flag = False
                        for i in self.TMS.get(str):
                            if i == str:
                                flag = True
                                break
                        if flag == True:
                            continue
                        self.status.append(str)
                        self.TMS[str].append(str)
                        self.assess_rules()
                        self.assess_rules()
                        continue
                    self.status.append(str)
                    self.TMS[str] = [str]
                    self.assess_rules()
                    self.assess_rules()
                    continue

            elif line.startswith('R'):
                # Rule
                pattern = re.search(r'Retract:(([\w+*-]*\w)->(-*\w))', line)
                if pattern:
                    if pattern.group(1) in self.status:
                        self.delete_rules(pattern.group(1), pattern.group(3))
                    continue

                pattern = re.search(r'Retract:(-*\w)', line)
                if pattern:
                    str = pattern.group(1)
                    if str in self.status:
                        if self.TMS.get(str):
                            for i in self.TMS.get(str):
                                if i == str:
                                    self.TMS[str].remove(i)
                                    break
                            self.delete_literals(str)
                            self.status.remove(str)
                            if not self.TMS[str]:
                                self.TMS.pop(str)
                            continue
                    continue

        print("Final Status of TMS:")
        myList.clear()

        for each in self.status:
            print(each)
            myList.append(each)

        return myList
