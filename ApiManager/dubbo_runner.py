import unittest
import json
import telnetlib
import socket
import re
import datetime
import logging
from ApiManager.models import TestCaseInfo


def select_case(id):
    obj = TestCaseInfo.objects.filter(id__in=id)
    obj_list=[]
    for index in obj:
        request = eval(index.request)
        body = request['test']['request']
        url = body.get('url')
        method = body.get('method')
        interface = body.get('DubboInterface')
        if body.get('json'):
            type,params='json',body.get('json')
        elif body.get('string'):
            type,params ='string',body.get('string')
        else:
            type,params='object',body.get('object')
        name=request['test']['name']
        try:
            validate=request['test']['validate'][0]['check']
        except:
            validate=None
        obj_dict={'url':url,'method':method,'interface':interface,type:params,
                  'name':name,'validate':validate}
        obj_list.append(obj_dict)
    return obj_list



def get_case_id(case_list):
    id_list=[]
    for case in case_list:
        id=case.split('=')[1]
        if id !='':
            id_list.append(id)
    return id_list


class dubboRunner(telnetlib.Telnet):
    def __init__(self, host=None, port=0):
        super().__init__(host, port)
        self.write(b'\n')

        self.status=None

    def command(self, flag, str_=""):
        data = self.read_until(flag.encode())
        self.write(str_.encode() + b"\n")
        return data

    def invoke(self, interface, method_name, name,validate,arg):
        arg = self.arg_modify(arg)
        Dubbo_request = {'interface': interface, 'method': method_name, 'data': tuple(arg)}

        if type(arg)==json:
            command_str = "invoke {0}.{1}({2})".format(interface, method_name, arg)
        if type(arg)==str:
            command_str='invoke {0}.{1}({2})'.format(interface, method_name, arg)
        if type(arg)==list:
            command_str='invoke {0}.{1}({2[0]},{2[1]})'.format(interface, method_name, arg)

        self.command('dubbo>', command_str)
        data = self.command('dubbo>', "")

        Dubbo_response = json.loads(data.decode('GBK',errors='ignore').split('\n')[0].strip())
        status=self.assert_dubbo(validate, Dubbo_response)
        return Dubbo_request,Dubbo_response,status

    def assert_dubbo(self,validate,Dubbo_response):
        try:
            assert None == re.search(str(validate),str(Dubbo_response)), '断言成功'#search里两边不相等则返回None
        except AssertionError as args:
            return '成功'
        else:
            return '失败'

    def summary(self,obj_list,Dubbo_request,Dubbo_response,spendTime=None,status=None,passNum=None,failNum=None):
        testResult = []

        summary_content = {"testPass": passNum,
                           "testName": "Dubbo测试报告",
                           "testAll": passNum + failNum,
                           "testFail": failNum,
                           "beginTime": str(datetime.datetime.now()),
                           "totalTime": self.sum_time(spendTime), "testSkip": 0}
        for index in range(0,len(obj_list)):
            response=str(Dubbo_response[index]).replace("'",'')
            testResult_content={'className':obj_list[index].get('interface'),
                                'methodName':obj_list[index].get('method'),
                                'description':obj_list[index].get('name'),
                                'log':['%s'%response],
                                "spendTime":spendTime[index],
                                "status":status[index]}

            testResult.append(testResult_content)
        summary_content['testResult']=testResult

        # self.__clear_env()
        return summary_content

    def arg_modify(self,arg):
        import ast
        for key,value in arg.items():
            if key=='json':
                return json.dumps(value)
            if key=='string':
                return value
            if key=='object':
                object_1,object_2=value.split('},')[0]+'}',value.split('},')[1]
                object_1=ast.literal_eval(object_1)
                value_list=[]
                value_list.append(object_1)
                value_list.append(object_2)
                return value_list

    def sum_time(self,time_ls):
        s=0
        for index in time_ls:
            s+=index
        return s

    def __clear_env(self):
        c = []
        for key in globals().keys():
            if not key.startswith("__"):
                c.append(key)
        for index in c:
            globals().pop(index)